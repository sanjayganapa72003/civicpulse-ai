from collections import defaultdict

from app.db.mongodb import db


citizen_requests_collection = db["citizen_requests"]


def get_district_demand():
    """
    Aggregate citizen requests by district and category.

    Returns:
        {
            "Tumkur": {
                "total_requests": 28,
                "road": 16,
                "water": 10,
                "healthcare": 2,

                "road_average_severity": 3.5,
                "water_average_severity": 3.2,
                "healthcare_average_severity": 3.8,

                "average_severity": 3.43
            }
        }
    """

    pipeline = [
        {
            "$group": {
                "_id": {
                    "district": "$location.district",
                    "category": "$category",
                },
                "request_count": {
                    "$sum": 1
                },
                "total_severity": {
                    "$sum": "$severity"
                },
            }
        }
    ]

    results = citizen_requests_collection.aggregate(pipeline)

    demand = defaultdict(
        lambda: {
            "total_requests": 0,
            "road": 0,
            "water": 0,
            "healthcare": 0,
            "road_total_severity": 0,
            "water_total_severity": 0,
            "healthcare_total_severity": 0,
            "total_severity": 0,
        }
    )

    for result in results:
        district = result["_id"]["district"]
        category = result["_id"]["category"]

        count = result["request_count"]
        severity = result["total_severity"]

        if district is None:
            continue

        demand[district]["total_requests"] += count
        demand[district]["total_severity"] += severity

        if category not in ("road", "water", "healthcare"):
            continue

        demand[district][category] += count

        severity_key = f"{category}_total_severity"
        demand[district][severity_key] += severity

    for district_data in demand.values():

        total_requests = district_data["total_requests"]

        if total_requests > 0:
            district_data["average_severity"] = round(
                district_data["total_severity"] / total_requests,
                2,
            )
        else:
            district_data["average_severity"] = 0.0

        for category in ("road", "water", "healthcare"):

            count = district_data[category]

            severity_key = f"{category}_total_severity"
            average_key = f"{category}_average_severity"

            if count > 0:
                district_data[average_key] = round(
                    district_data[severity_key] / count,
                    2,
                )
            else:
                district_data[average_key] = 0.0

            del district_data[severity_key]

        del district_data["total_severity"]

    return dict(demand)