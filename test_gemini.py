import json
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

test_requests = [
    "The roads in bagalkot are badly damaged."
]

for text in test_requests:

    prompt = f"""
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

    Canonical Karnataka district names used by CivicPulse:

    - Bagalkot
    - Bangalore
    - Bangalore Rural
    - Belgaum
    - Bellary
    - Bidar
    - Bijapur
    - Chamarajanagar
    - Chikkaballapura
    - Chikmagalur
    - Chitradurga
    - Dakshina Kannada
    - Davanagere
    - Dharwad
    - Gadag
    - Gulbarga
    - Hassan
    - Haveri
    - Kolar
    - Kodagu
    - Koppal
    - Mandya
    - Mysore
    - Raichur
    - Ramanagara
    - Shimoga
    - Tumkur
    - Udupi
    - Uttara Kannada
    - Vijayanagar
    - Yadgir

    DISTRICT NORMALIZATION RULES:

    - The district field MUST use one of the canonical district names above.
    - Normalize common alternative names and spellings.

    Examples:

    Davangere -> Davanagere
    Davanagere -> Davanagere

    Vijayapura -> Bijapur
    Bijapur -> Bijapur

    Kalaburagi -> Gulbarga
    Gulbarga -> Gulbarga

    Belagavi -> Belgaum
    Belgaum -> Belgaum

    Ballari -> Bellary
    Bellary -> Bellary

    Bengaluru -> Bangalore
    Bengaluru Urban -> Bangalore
    Bengaluru Rural -> Bangalore Rural

    Mysuru -> Mysore
    Mysore -> Mysore

    Shivamogga -> Shimoga
    Shimoga -> Shimoga

    Tumakuru -> Tumkur
    Tumkur -> Tumkur

    Chikkamagaluru -> Chikmagalur
    Chikmagalur -> Chikmagalur

    Bagalkote -> Bagalkot
    Bagalkot -> Bagalkot

    Do NOT guess the district.

    If the district is not explicitly mentioned in the citizen request,
    return null.

    Extract taluk and village only when explicitly mentioned.
    Do not guess them.

    Return exactly:

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
    {text}
    """

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )

    result = response.text.strip()

    if result.startswith("```"):
        result = result.replace("```json", "", 1)
        result = result.replace("```", "", 1)
        result = result.strip()

    parsed = json.loads(result)

    print("\nCitizen request:")
    print(text)

    print("Extracted:")
    print(json.dumps(parsed, indent=2, ensure_ascii=False))