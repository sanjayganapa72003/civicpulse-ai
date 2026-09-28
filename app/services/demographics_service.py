from app.db.mongodb import demographics_collection


def get_demographics(district: str):
    return demographics_collection.find_one(
        {
            "state": "Karnataka",
            "district": district,
        },
        {
            "_id": 0,
        },
    )