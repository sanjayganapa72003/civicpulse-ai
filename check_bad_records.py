from app.db.mongodb import citizen_requests_collection

cursor = citizen_requests_collection.find(
    {
        "location.district": {
            "$in": ["bagalkot", "bijapur"]
        }
    },
    {
        "_id": 1,
        "raw_text": 1,
        "category": 1,
        "severity": 1,
        "source": 1,
        "data_type": 1,
        "created_at": 1,
        "location": 1,
    },
)

for doc in cursor:
    print("\n-----------------------------")
    print("ID:", doc["_id"])
    print("Text:", doc.get("raw_text"))
    print("Category:", doc.get("category"))
    print("Severity:", doc.get("severity"))
    print("Source:", doc.get("source"))
    print("Data type:", doc.get("data_type"))
    print("Created:", doc.get("created_at"))
    print("Location:", doc.get("location"))