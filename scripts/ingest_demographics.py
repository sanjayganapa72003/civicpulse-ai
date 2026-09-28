import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from dotenv import load_dotenv

from app.db.mongodb import demographics_collection
from app.models.demographics import DemographicRecord


load_dotenv()


PROCESSED_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "demographics.csv"
)


def load_processed_data():
    """Load normalized demographic data from CSV."""

    return pd.read_csv(PROCESSED_FILE)


def validate_data(df):
    """Validate required columns and basic demographic consistency."""

    required_columns = [
        "state",
        "district",
        "population",
        "rural_population",
        "urban_population",
        "households",
        "data_year",
        "source",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    if df.empty:
        raise ValueError("Demographics CSV is empty.")

    # Population consistency check
    population_valid = (
        df["population"]
        == df["rural_population"] + df["urban_population"]
    )

    if not population_valid.all():
        invalid = df.loc[~population_valid, "district"].tolist()

        raise ValueError(
            f"Population mismatch for districts: {invalid}"
        )

    # We expect one record per district
    if df["district"].duplicated().any():
        duplicates = (
            df.loc[
                df["district"].duplicated(),
                "district"
            ]
            .tolist()
        )

        raise ValueError(
            f"Duplicate districts found: {duplicates}"
        )

    print(f"Validated {len(df)} demographic records.")


def save_to_mongodb(df):
    """Validate each record and upsert into MongoDB."""

    inserted_count = 0

    for record in df.to_dict(orient="records"):

        demographic = DemographicRecord(
            state=record["state"],
            district=record["district"],
            population=int(record["population"]),
            rural_population=int(record["rural_population"]),
            urban_population=int(record["urban_population"]),
            households=int(record["households"]),
            data_year=int(record["data_year"]),
            source=record["source"],
        )

        demographics_collection.replace_one(
            {
                "state": demographic.state,
                "district": demographic.district,
                "data_year": demographic.data_year,
            },
            demographic.model_dump(),
            upsert=True,
        )

        inserted_count += 1

    print(
        f"Successfully upserted "
        f"{inserted_count} records into MongoDB."
    )


def main():

    if not PROCESSED_FILE.exists():
        raise FileNotFoundError(
            f"Processed demographics file not found:\n"
            f"{PROCESSED_FILE}"
        )

    print("Loading processed demographics...")

    df = load_processed_data()

    print(f"Records loaded: {len(df)}")

    validate_data(df)

    save_to_mongodb(df)


if __name__ == "__main__":
    main()