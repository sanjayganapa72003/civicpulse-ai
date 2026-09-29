import json
import os
import time
from typing import Any

from dotenv import load_dotenv
from google import genai

from app.services.rag_retrieval_service import retrieve_policy_chunks


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# Primary policy-generation model.
PRIMARY_MODEL = "gemini-3.6-flash"

# Fallback policy-generation model.
FALLBACK_MODEL = "gemini-3.5-flash-lite"


POLICY_SYNTHESIS_PROMPT = """
You are a policy-evidence assistant for a government development
intelligence platform.

Your job is to explain how the retrieved Indian government documents
relate to a development need identified from citizen demand and
infrastructure data.

IMPORTANT RULES:

1. Use ONLY the supplied government evidence for claims about
   government policies, programmes, guidelines, standards, targets,
   implementation frameworks, or schemes.

2. Do NOT invent:
   - government schemes
   - funding amounts
   - targets
   - deadlines
   - eligibility criteria
   - district-specific government decisions
   - project recommendations that are not supported by the evidence

3. Do NOT calculate or modify the priority score.

4. Do NOT decide whether a project should definitely be funded.

5. Clearly distinguish:
   - development evidence from the platform
   - government evidence from retrieved documents

6. If the retrieved documents do not provide enough evidence,
   explicitly say so.

7. Cite the relevant document and page number when describing
   government evidence.

8. Keep the explanation concise and suitable for a policymaker.

Return ONLY valid JSON in exactly this structure:

{{
    "answer": "concise policy relevance explanation",
    "evidence": [
        {{
            "document": "document title",
            "page": 1,
            "claim": "what the government document says"
        }}
    ],
    "limitations": [
        "important limitation or missing evidence"
    ]
}}

Development context:
{development_context}

Retrieved government evidence:
{government_evidence}

Policy retrieval query:
{query}
"""


def _clean_json_response(text: str) -> str:
    """
    Clean Gemini's response so it can be parsed as JSON.
    """

    text = text.strip()

    if text.startswith("```json"):
        text = text[len("```json"):].strip()

    elif text.startswith("```"):
        text = text[len("```"):].strip()

    if text.endswith("```"):
        text = text[:-3].strip()

    # Handle accidental text before/after the JSON object.
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:
        text = text[start:end + 1]

    return text


def _generate_with_model(
    model: str,
    prompt: str,
) -> dict[str, Any]:
    """
    Generate a policy answer using a specific Gemini model.

    Raises an exception if generation or JSON parsing fails.
    """

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            "response_mime_type": "application/json"
        },
    )

    if not response.text:
        raise ValueError(
            f"Gemini model {model} returned an empty response."
        )

    result = _clean_json_response(response.text)

    parsed = json.loads(result)

    return {
        "answer": parsed.get("answer", ""),
        "evidence": parsed.get("evidence", []),
        "limitations": parsed.get("limitations", []),
    }


def _generate_with_retries(
    model: str,
    prompt: str,
    max_attempts: int = 3,
) -> dict[str, Any]:
    """
    Try one Gemini model multiple times.

    Uses exponential backoff between attempts.
    """

    last_error = None

    for attempt in range(max_attempts):

        try:
            print(
                f"[Policy Generation] "
                f"Model={model}, "
                f"Attempt={attempt + 1}/{max_attempts}"
            )

            result = _generate_with_model(
                model=model,
                prompt=prompt,
            )

            print(
                f"[Policy Generation] "
                f"Successfully generated using {model}"
            )

            return result

        except Exception as exc:

            last_error = exc

            print(
                f"[Policy Generation] "
                f"Model={model}, "
                f"Attempt={attempt + 1} failed: "
                f"{type(exc).__name__}: {exc}"
            )

            error_text = str(exc)

            # Don't waste all attempts if the API explicitly reports
            # quota/rate-limit exhaustion.
            if (
                "429" in error_text
                or "RESOURCE_EXHAUSTED" in error_text
            ):
                print(
                    f"[Policy Generation] "
                    f"Quota/rate limit detected for {model}. "
                    f"Moving to fallback."
                )
                break

            # Retry transient failures.
            if attempt < max_attempts - 1:
                sleep_seconds = 2 ** attempt

                print(
                    f"[Policy Generation] "
                    f"Retrying {model} in "
                    f"{sleep_seconds} seconds..."
                )

                time.sleep(sleep_seconds)

    raise last_error


def generate_policy_answer(
    query: str,
    top_k: int = 5,
    development_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Retrieve government evidence and generate a grounded
    policy-relevance explanation using Gemini.

    Generation strategy:

        Primary model
            ↓
        3 attempts
            ↓
        if unsuccessful
            ↓
        Fallback model
            ↓
        3 attempts
    """

    # ---------------------------------------------------------
    # 1. Retrieve government evidence
    # ---------------------------------------------------------

    retrieved_chunks = retrieve_policy_chunks(
        query=query,
        top_k=top_k,
    )

    if not retrieved_chunks:
        return {
            "answer": (
                "No relevant government policy evidence "
                "was retrieved for this development need."
            ),
            "evidence": [],
            "limitations": [
                "No relevant policy documents were retrieved."
            ],
        }

    # ---------------------------------------------------------
    # 2. Prepare retrieved evidence
    # ---------------------------------------------------------

    government_evidence = []

    for chunk in retrieved_chunks:
        government_evidence.append(
            {
                "document": chunk.get("title"),
                "page": chunk.get("page"),
                "section": chunk.get("section"),
                "domain": chunk.get("domain"),
                "source": chunk.get("source"),
                "relevance_score": chunk.get("score"),
                "text": chunk.get("text"),
            }
        )

    # ---------------------------------------------------------
    # 3. Build synthesis prompt
    # ---------------------------------------------------------

    prompt = POLICY_SYNTHESIS_PROMPT.format(
        development_context=json.dumps(
            development_context or {},
            ensure_ascii=False,
            indent=2,
        ),
        government_evidence=json.dumps(
            government_evidence,
            ensure_ascii=False,
            indent=2,
        ),
        query=query,
    )

    # ---------------------------------------------------------
    # 4. Try primary Gemini model
    # ---------------------------------------------------------

    try:

        return _generate_with_retries(
            model=PRIMARY_MODEL,
            prompt=prompt,
            max_attempts=3,
        )

    except Exception as primary_error:

        print(
            "[Policy Generation] "
            f"Primary model {PRIMARY_MODEL} failed completely: "
            f"{type(primary_error).__name__}: {primary_error}"
        )

    # ---------------------------------------------------------
    # 5. Try fallback Gemini model
    # ---------------------------------------------------------

    try:

        return _generate_with_retries(
            model=FALLBACK_MODEL,
            prompt=prompt,
            max_attempts=3,
        )

    except Exception as fallback_error:

        print(
            "[Policy Generation] "
            f"Fallback model {FALLBACK_MODEL} failed completely: "
            f"{type(fallback_error).__name__}: {fallback_error}"
        )

        return {
            "answer": (
                "Policy synthesis could not be completed."
            ),
            "evidence": [],
            "limitations": [
                (
                    "Gemini policy synthesis failed after "
                    "trying both the primary and fallback models."
                ),
                f"Primary model error: {str(primary_error)}",
                f"Fallback model error: {str(fallback_error)}",
            ],
        }