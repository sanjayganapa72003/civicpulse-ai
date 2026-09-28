from collections import defaultdict

from app.db.mongodb import db


infrastructure_collection = db["infrastructure"]
demographics_collection = db["demographics"]


def get_district_infrastructure():
    infrastructure_cursor = infrastructure_collection.find(
        {},
        {
            "_id": 0,
            "state": 1,
            "district": 1,
            "category": 1,
            "indicators": 1,
            "data_year": 1,
            "source": 1,
            "source_url": 1,
        },
    )

    infrastructure = defaultdict(dict)

    for record in infrastructure_cursor:
        district = record["district"]
        category = record["category"]

        infrastructure[district][category] = {
            "indicators": record["indicators"],
            "data_year": record["data_year"],
            "source": record["source"],
            "source_url": record["source_url"],
        }

    demographics_cursor = demographics_collection.find(
        {},
        {
            "_id": 0,
            "district": 1,
            "population": 1,
            "rural_population": 1,
            "urban_population": 1,
            "households": 1,
            "data_year": 1,
            "source": 1,
        },
    )

    demographics = {}

    for record in demographics_cursor:
        demographics[record["district"]] = {
            "population": record["population"],
            "rural_population": record["rural_population"],
            "urban_population": record["urban_population"],
            "households": record["households"],
            "data_year": record["data_year"],
            "source": record["source"],
        }

    result = {}

    all_districts = set(infrastructure.keys()) | set(demographics.keys())

    for district in all_districts:
        result[district] = {
            "infrastructure": dict(infrastructure.get(district, {})),
            "demographics": demographics.get(district),
        }

    return result