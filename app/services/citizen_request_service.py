import json
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# Primary model for citizen-request extraction.
PRIMARY_MODEL = "gemini-3.6-flash"

# Lightweight fallback model for high-throughput structured extraction.
FALLBACK_MODEL = "gemini-3.5-flash-lite"


KARNATAKA_DISTRICTS = """
Bagalkot
Bangalore
Bangalore Rural
Belgaum
Bellary
Bidar
Bijapur
Chamarajanagar
Chikkaballapura
Chikmagalur
Chitradurga
Dakshina Kannada
Davanagere
Dharwad
Gadag
Gulbarga
Hassan
Haveri
Kolar
Kodagu
Koppal
Mandya
Mysore
Raichur
Ramanagara
Shimoga
Tumkur
Udupi
Uttara Kannada
Vijayanagar
Yadgir
"""


EXTRACTION_PROMPT = f"""
You are an information extraction system for CivicPulse AI,
a citizen-demand intelligence platform for Karnataka.

Analyze the citizen request and return ONLY valid JSON.

Allowed languages:
- english
- hindi
- kannada

Allowed categories:
- road
- water
- healthcare

Severity:
1 = minor
2 = low
3 = moderate
4 = serious
5 = critical

KARNATAKA DISTRICTS

The following are the canonical district names used by the
CivicPulse database:

{KARNATAKA_DISTRICTS}

DISTRICT NORMALIZATION RULES:

- The extracted district MUST match one of the canonical names above.
- Normalize common alternative names, spellings, and transliterations
  to the corresponding canonical district.

Examples:

    Davangere -> Davanagere
    Davanagere -> Davanagere
    Vijayapura -> Bijapur
    Bijapur -> Bijapur
    Kalaburagi -> Gulbarga
    Gulbarga -> Gulbarga
    Belagavi -> Belgaum
    Belgaum -> Belgaum
    Bengaluru -> Bangalore
    Bengaluru Rural -> Bangalore Rural
    Mysuru -> Mysore
    Shivamogga -> Shimoga
    Tumakuru -> Tumkur
    Chikkamagaluru -> Chikmagalur
    Bagalkote -> Bagalkot

IMPORTANT:

- Do NOT invent or guess a district.
- Extract a district only when it is explicitly mentioned
  or can be directly identified from the citizen's request.
- If the district is not mentioned, return null.
- Extract location only when explicitly mentioned.
- Do not guess a taluk or village.
- If taluk is not explicitly mentioned, return null.
- If village is not explicitly mentioned, return null.
- The category MUST be one of:
    road
    water
    healthcare
- Severity MUST be an integer from 1 to 5.

RETURN EXACTLY THIS STRUCTURE:

{{
    "language": "english | hindi | kannada",
    "category": "road | water | healthcare",
    "issue_type": "string",
    "district": "canonical district name or null",
    "taluk": "string or null",
    "village": "string or null",
    "severity": 1
}}

Citizen request:
"""


def clean_json_response(result: str) -> dict:
    """
    Clean Gemini's response and convert it into a Python dictionary.
    """

    result = result.strip()

    # Gemini may return JSON inside Markdown code fences.
    if result.startswith("```"):
        result = result.replace("```json", "", 1)
        result = result.replace("```JSON", "", 1)
        result = result.replace("```", "", 1)
        result = result.strip()

    return json.loads(result)


async def extract_citizen_request(text: str) -> dict:
    """
    Extract structured information from a citizen request.

    Primary model:
        gemini-3.6-flash

    Fallback model:
        gemini-3.5-flash-lite

    If the primary model is temporarily unavailable, the fallback
    model is attempted automatically.
    """

    models = [
        PRIMARY_MODEL,
        FALLBACK_MODEL,
    ]

    last_error = None

    for model in models:

        try:
            print(
                f"[Citizen Extraction] Trying model: {model}"
            )

            response = client.models.generate_content(
                model=model,
                contents=EXTRACTION_PROMPT + text,
            )

            if not response.text:
                raise ValueError(
                    f"Model {model} returned an empty response"
                )

            result = response.text.strip()

            parsed = clean_json_response(result)

            print(
                f"[Citizen Extraction] Successfully extracted "
                f"using model: {model}"
            )

            print(
                f"[Citizen Extraction] Result: {parsed}"
            )

            return parsed

        except Exception as exc:

            last_error = exc

            print(
                f"[Citizen Extraction] Model {model} failed: {exc}"
            )

            # Continue to the fallback model.
            continue

    # Both models failed.
    print(
        "[Citizen Extraction] All extraction models failed."
    )

    raise last_error