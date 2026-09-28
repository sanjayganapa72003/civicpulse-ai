from app.db.mongodb import citizen_requests_collection


updates = {
    "bagalkot": "Bagalkot",
    "bijapur": "Bijapur",
}

for old_district, new_district in updates.items():
    result = citizen_requests_collection.update_many(
        {"location.district": old_district},
        {
            "$set": {
                "location.district": new_district
            }
        }
    )

    print(
        f"{old_district} -> {new_district}: "
        f"{result.modified_count} document(s) updated"
    )