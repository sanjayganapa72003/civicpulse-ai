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

MODEL = "gemini-3.6-flash"


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
    text = text.strip()

    if text.startswith("```json"):
        text = text[len("```json"):].strip()
    elif text.startswith("```"):
        text = text[len("```"):].strip()

    if text.endswith("```"):
        text = text[:-3].strip()

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:
        text = text[start:end + 1]

    return text


def generate_policy_answer(
    query: str,
    top_k: int = 5,
    development_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Retrieve government evidence and generate a grounded
    policy-relevance explanation using Gemini.
    """

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

    last_error = None

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config={
                    "response_mime_type": "application/json"
                },
            )

            result = _clean_json_response(
                response.text
            )

            parsed = json.loads(result)

            return {
                "answer": parsed.get("answer", ""),
                "evidence": parsed.get("evidence", []),
                "limitations": parsed.get("limitations", []),
            }

        except Exception as exc:
            last_error = exc

            print(
                f"[Policy Generation] Attempt {attempt + 1} failed: "
                f"{type(exc).__name__}: {exc}"
            )

            # Do not retry when Gemini quota/rate limit is exhausted
            if "429" in str(exc) or "RESOURCE_EXHAUSTED" in str(exc):
                break

            if attempt < 2:
                time.sleep(2 ** attempt)

    return {
        "answer": (
            "Policy synthesis could not be completed."
        ),
        "evidence": [],
        "limitations": [
            f"Gemini policy synthesis failed: {str(last_error)}"
        ],
    }