from collections import Counter

from app.db.mongodb import citizen_requests_collection


CANONICAL_DISTRICTS = {
    "Bagalkot",
    "Bangalore",
    "Bangalore Rural",
    "Belgaum",
    "Bellary",
    "Bidar",
    "Bijapur",
    "Chamarajanagar",
    "Chikkaballapura",
    "Chikmagalur",
    "Chitradurga",
    "Dakshina Kannada",
    "Davanagere",
    "Dharwad",
    "Gadag",
    "Gulbarga",
    "Hassan",
    "Haveri",
    "Kolar",
    "Kodagu",
    "Koppal",
    "Mandya",
    "Mysore",
    "Raichur",
    "Ramanagara",
    "Shimoga",
    "Tumkur",
    "Udupi",
    "Uttara Kannada",
    "Vijayanagar",
    "Yadgir",
}

districts = Counter()

cursor = citizen_requests_collection.find(
    {"location.district": {"$exists": True}},
    {"location.district": 1, "raw_text": 1, "source": 1, "data_type": 1},
)

for doc in cursor:
    district = doc.get("location", {}).get("district")

    if district:
        districts[district] += 1

print("\nDistrict values currently stored:\n")

for district, count in sorted(districts.items()):
    status = "CANONICAL" if district in CANONICAL_DISTRICTS else "NON-CANONICAL"
    print(f"{district:25} {count:4}  {status}")

print("\nNon-canonical values:\n")

for district, count in sorted(districts.items()):
    if district not in CANONICAL_DISTRICTS:
        print(f"{district:25} {count}")