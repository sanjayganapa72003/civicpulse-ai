import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.db.mongodb import db


citizen_requests_collection = db["citizen_requests"]


# Districts that exist in our infrastructure/demographic data.
# We deliberately give some districts higher weights so that
# synthetic demand hotspots emerge naturally.
DISTRICTS = {
    "Bangalore": 1.0,
    "Bangalore Rural": 1.8,
    "Belgaum": 1.7,
    "Bellary": 1.5,
    "Mysore": 1.6,
    "Tumkur": 1.4,
    "Gulbarga": 1.5,
    "Raichur": 1.3,
    "Davanagere": 1.2,
    "Kolar": 1.2,
    "Mandya": 1.0,
    "Hassan": 1.0,
    "Shimoga": 1.0,
    "Chikmagalur": 0.9,
    "Chitradurga": 1.1,
}


REQUESTS = {
    "road": {
        "english": [
            "Our village roads are badly damaged and difficult to travel on.",
            "The road connecting our village to the main road is in poor condition.",
            "Ambulances cannot reach our village easily because of the damaged roads.",
            "There is no proper road connectivity to our village.",
            "The road becomes very difficult to use during the rainy season.",
        ],
        "hindi": [
            "हमारे गांव की सड़कें बहुत खराब हैं और यात्रा करना मुश्किल है।",
            "हमारे गांव को मुख्य सड़क से जोड़ने वाली सड़क बहुत खराब है।",
            "खराब सड़क के कारण एम्बुलेंस हमारे गांव तक आसानी से नहीं पहुंच पाती।",
            "हमारे गांव में सड़क की उचित सुविधा नहीं है।",
        ],
        "kannada": [
            "ನಮ್ಮ ಗ್ರಾಮದ ರಸ್ತೆಗಳು ತುಂಬಾ ಹದಗೆಟ್ಟಿವೆ ಮತ್ತು ಪ್ರಯಾಣಿಸಲು ಕಷ್ಟವಾಗುತ್ತಿದೆ.",
            "ನಮ್ಮ ಗ್ರಾಮವನ್ನು ಮುಖ್ಯ ರಸ್ತೆಗೆ ಸಂಪರ್ಕಿಸುವ ರಸ್ತೆ ಸರಿಯಾದ ಸ್ಥಿತಿಯಲ್ಲಿಲ್ಲ.",
            "ಕೆಟ್ಟ ರಸ್ತೆಯಿಂದಾಗಿ ಆಂಬ್ಯುಲೆನ್ಸ್ ನಮ್ಮ ಗ್ರಾಮಕ್ಕೆ ಸುಲಭವಾಗಿ ಬರಲು ಸಾಧ್ಯವಾಗುತ್ತಿಲ್ಲ.",
            "ನಮ್ಮ ಗ್ರಾಮಕ್ಕೆ ಸರಿಯಾದ ರಸ್ತೆ ಸಂಪರ್ಕ ಇಲ್ಲ.",
            "ಮಳೆಗಾಲದಲ್ಲಿ ನಮ್ಮ ಗ್ರಾಮದ ರಸ್ತೆ ಬಳಸಲು ತುಂಬಾ ಕಷ್ಟವಾಗುತ್ತದೆ.",
        ],
    },
    "water": {
        "english": [
            "Our village does not have a reliable drinking water supply.",
            "Many households in our area do not have tap water.",
            "We have to travel far to collect drinking water.",
            "Water supply is irregular in our village.",
            "Our village needs better household tap water coverage.",
        ],
        "hindi": [
            "हमारे गांव में पीने के पानी की नियमित सुविधा नहीं है।",
            "हमारे क्षेत्र के कई घरों में नल का पानी नहीं है।",
            "पीने का पानी लाने के लिए हमें बहुत दूर जाना पड़ता है।",
            "हमारे गांव में पानी की आपूर्ति नियमित नहीं है।",
        ],
        "kannada": [
            "ನಮ್ಮ ಗ್ರಾಮದಲ್ಲಿ ಕುಡಿಯುವ ನೀರಿನ ಸರಿಯಾದ ಪೂರೈಕೆ ಇಲ್ಲ.",
            "ನಮ್ಮ ಪ್ರದೇಶದ ಅನೇಕ ಮನೆಗಳಿಗೆ ನಳದ ನೀರಿನ ಸಂಪರ್ಕ ಇಲ್ಲ.",
            "ಕುಡಿಯುವ ನೀರು ತರಲು ನಾವು ಬಹಳ ದೂರ ಹೋಗಬೇಕಾಗಿದೆ.",
            "ನಮ್ಮ ಗ್ರಾಮದಲ್ಲಿ ನೀರಿನ ಪೂರೈಕೆ ನಿಯಮಿತವಾಗಿಲ್ಲ.",
            "ನಮ್ಮ ಗ್ರಾಮಕ್ಕೆ ಉತ್ತಮ ಮನೆ ನಳ ಸಂಪರ್ಕದ ಅಗತ್ಯವಿದೆ.",
        ],
    },
    "healthcare": {
        "english": [
            "Our village does not have adequate healthcare facilities.",
            "People have to travel far to reach a hospital.",
            "Emergency healthcare is difficult to access in our area.",
            "There are not enough healthcare facilities for our population.",
            "Patients have difficulty reaching hospitals from our village.",
        ],
        "hindi": [
            "हमारे गांव में पर्याप्त स्वास्थ्य सुविधाएं नहीं हैं।",
            "अस्पताल पहुंचने के लिए लोगों को बहुत दूर जाना पड़ता है।",
            "हमारे क्षेत्र में आपातकालीन स्वास्थ्य सेवा आसानी से उपलब्ध नहीं है।",
            "हमारे क्षेत्र की आबादी के लिए स्वास्थ्य सुविधाएं पर्याप्त नहीं हैं।",
        ],
        "kannada": [
            "ನಮ್ಮ ಗ್ರಾಮದಲ್ಲಿ ಸಾಕಷ್ಟು ಆರೋಗ್ಯ ಸೌಲಭ್ಯಗಳಿಲ್ಲ.",
            "ಆಸ್ಪತ್ರೆಗೆ ಹೋಗಲು ಜನರು ಬಹಳ ದೂರ ಪ್ರಯಾಣಿಸಬೇಕಾಗಿದೆ.",
            "ನಮ್ಮ ಪ್ರದೇಶದಲ್ಲಿ ತುರ್ತು ಆರೋಗ್ಯ ಸೇವೆ ಪಡೆಯಲು ಕಷ್ಟವಾಗುತ್ತಿದೆ.",
            "ನಮ್ಮ ಜನಸಂಖ್ಯೆಗೆ ಸಾಕಷ್ಟು ಆರೋಗ್ಯ ಸೌಲಭ್ಯಗಳಿಲ್ಲ.",
            "ನಮ್ಮ ಗ್ರಾಮದಿಂದ ಆಸ್ಪತ್ರೆಗೆ ಹೋಗಲು ರೋಗಿಗಳಿಗೆ ತೊಂದರೆಯಾಗುತ್ತಿದೆ.",
        ],
    },
}


ISSUE_TYPES = {
    "road": [
        "poor_road_condition",
        "poor_connectivity",
        "emergency_access",
    ],
    "water": [
        "water_shortage",
        "lack_of_tap_connection",
        "irregular_water_supply",
    ],
    "healthcare": [
        "hospital_access",
        "insufficient_healthcare_facilities",
        "emergency_healthcare_access",
    ],
}


LANGUAGE_WEIGHTS = {
    "english": 0.25,
    "hindi": 0.20,
    "kannada": 0.55,
}


CATEGORY_WEIGHTS = {
    "road": 0.40,
    "water": 0.35,
    "healthcare": 0.25,
}


def weighted_choice(options):
    values = list(options.keys())
    weights = list(options.values())

    return random.choices(values, weights=weights, k=1)[0]


def choose_language():
    return weighted_choice(LANGUAGE_WEIGHTS)


def choose_category():
    return weighted_choice(CATEGORY_WEIGHTS)


def choose_district():
    return weighted_choice(DISTRICTS)


def choose_severity():
    return random.choices(
        [1, 2, 3, 4, 5],
        weights=[5, 15, 30, 35, 15],
        k=1,
    )[0]


def generate_request():
    district = choose_district()
    category = choose_category()
    language = choose_language()

    text = random.choice(REQUESTS[category][language])
    issue_type = random.choice(ISSUE_TYPES[category])
    severity = choose_severity()

    # Create synthetic taluk/village names.
    # These are explicitly synthetic and should not be treated
    # as real administrative names.
    taluk = f"Synthetic Taluk {random.randint(1, 8)}"
    village = f"Synthetic Village {random.randint(1, 40)}"

    created_at = datetime.now(timezone.utc) - timedelta(
        days=random.randint(0, 90),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )

    return {
        "raw_text": text,
        "language": language,
        "category": category,
        "issue_type": issue_type,
        "severity": severity,
        "location": {
            "state": "Karnataka",
            "district": district,
            "taluk": taluk,
            "village": village,
        },
        "source": "synthetic",
        "data_type": "synthetic",
        "created_at": created_at,
    }


def main():
    random.seed(42)

    number_of_requests = 300

    documents = [
        generate_request()
        for _ in range(number_of_requests)
    ]

    result = citizen_requests_collection.insert_many(documents)

    print(f"Synthetic requests inserted: {len(result.inserted_ids)}")

    print(
        "Total citizen requests:",
        citizen_requests_collection.count_documents({})
    )


if __name__ == "__main__":
    main()