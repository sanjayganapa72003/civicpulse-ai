import sys
import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

from app.db.mongodb import db
from app.models.infrastructure import InfrastructureRecord


PROCESSED_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "roads.csv"
)

infrastructure_collection = db["infrastructure"]


DISTRICT_MAPPING = {
    "Bangalore R": "Bangalore Rural",
    "Bangalore U": "Bangalore",
    "Chickballapur": "Chikkaballapura",
    "Chickmagalur": "Chikmagalur",
    "Ramnagar": "Ramanagara",
}


def load_data():
    return pd.read_csv(PROCESSED_FILE)


def normalize_district(district):
    return DISTRICT_MAPPING.get(
        district,
        district,
    )


def validate_data(df):

    required_columns = [
        "state",
        "district",
        "category",
        "indicators",
        "data_year",
        "source",
        "source_url",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )

    if df.empty:
        raise ValueError(
            "Road dataset is empty."
        )


def ingest_data(df):

    count = 0
    skipped = 0

    for record in df.to_dict(orient="records"):

        original_district = str(
            record["district"]
        ).strip()

        # "Total" is a statewide aggregate,
        # not a district-level record.
        if original_district == "Total":
            skipped += 1
            continue

        canonical_district = normalize_district(
            original_district
        )

        indicators = ast.literal_eval(
            record["indicators"]
        )

        infrastructure = InfrastructureRecord(
            state=record["state"],
            district=canonical_district,
            category=record["category"],
            indicators=indicators,
            data_year=int(record["data_year"]),
            source=record["source"],
            source_url=record["source_url"],
        )

        infrastructure_collection.replace_one(
            {
                "state": infrastructure.state,
                "district": infrastructure.district,
                "category": infrastructure.category,
                "data_year": infrastructure.data_year,
            },
            infrastructure.model_dump(),
            upsert=True,
        )

        count += 1

    print(
        f"Successfully upserted {count} "
        f"district road records."
    )

    print(
        f"Skipped {skipped} statewide records."
    )


def cleanup_old_records():

    result = infrastructure_collection.delete_many(
        {
            "category": "road",
            "district": {
                "$in": [
                    "Bangalore R",
                    "Bangalore U",
                    "Chickballapur",
                    "Chickmagalur",
                    "Ramnagar",
                    "Total",
                ]
            },
        }
    )

    print(
        f"Removed {result.deleted_count} "
        f"old/non-canonical road records."
    )


def main():

    if not PROCESSED_FILE.exists():
        raise FileNotFoundError(
            f"File not found: {PROCESSED_FILE}"
        )

    print("Loading processed road data...")

    df = load_data()

    print(
        f"Records loaded: {len(df)}"
    )

    validate_data(df)

    # Remove previously inserted records that
    # use non-canonical district names.
    cleanup_old_records()

    ingest_data(df)


if __name__ == "__main__":
    main()