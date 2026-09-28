import ast
import sys
from pathlib import Path

import pandas as pd

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from app.db.mongodb import db
from app.models.infrastructure import InfrastructureRecord


PROCESSED_FILE = PROJECT_ROOT / "data" / "processed" / "healthcare.csv"

infrastructure_collection = db["infrastructure"]


def ingest_healthcare():
    df = pd.read_csv(PROCESSED_FILE)

    required_columns = {
        "state",
        "district",
        "category",
        "indicators",
        "data_year",
        "source",
        "source_url",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(f"Missing columns: {missing_columns}")

    inserted = 0

    for _, row in df.iterrows():

        indicators = ast.literal_eval(row["indicators"])

        record = InfrastructureRecord(
            state=row["state"],
            district=row["district"],
            category=row["category"],
            indicators=indicators,
            data_year=int(row["data_year"]),
            source=row["source"],
            source_url=row["source_url"],
        )

        infrastructure_collection.replace_one(
            {
                "state": record.state,
                "district": record.district,
                "category": record.category,
                "data_year": record.data_year,
            },
            record.model_dump(),
            upsert=True,
        )

        inserted += 1

    print(f"Healthcare records processed: {inserted}")


if __name__ == "__main__":
    ingest_healthcare()
    