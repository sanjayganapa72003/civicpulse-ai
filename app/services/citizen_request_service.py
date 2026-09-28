import json
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL = "gemini-3.6-flash"

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
- For example:
    - Davangere -> Davanagere
    - Davanagere -> Davanagere
    - Vijayapura -> Bijapur
    - Bijapur -> Bijapur
    - Kalaburagi -> Gulbarga
    - Gulbarga -> Gulbarga
    - Belagavi -> Belgaum
    - Belgaum -> Belgaum
    - Bengaluru -> Bangalore
    - Bengaluru Rural -> Bangalore Rural
    - Mysuru -> Mysore
    - Shivamogga -> Shimoga
    - Tumakuru -> Tumkur
    - Chikkamagaluru -> Chikmagalur
    - Bagalkote -> Bagalkot

- Do NOT invent or guess a district.
- Extract a district only when it is explicitly mentioned
  or can be directly identified from the citizen's request.
- If the district is not mentioned, return null.

Extract location only when explicitly mentioned.
Do not guess a taluk or village.

Return exactly this structure:

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


async def extract_citizen_request(text: str) -> dict:

    response = client.models.generate_content(
        model=MODEL,
        contents=EXTRACTION_PROMPT + text,
    )

    result = response.text.strip()

    # Gemini may return JSON inside Markdown code fences.
    if result.startswith("```"):
        result = result.replace("```json", "", 1)
        result = result.replace("```", "", 1)
        result = result.strip()

    return json.loads(result)