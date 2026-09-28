import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd


RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "roads"
    / "RS_Session_265_AU_620_D.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "roads.csv"
)


def main():

    print("Loading road dataset...")

    df = pd.read_csv(RAW_FILE)

    print(f"Source records: {len(df)}")

    required_columns = [
        "Sl.No.",
        "District Name",
        "Road Length Sanctioned",
        "Road Length Completed",
        "Balance Road Length",
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

    records = []

    for _, row in df.iterrows():

        records.append(
            {
                "state": "Karnataka",
                "district": str(row["District Name"]).strip(),
                "category": "road",
                "indicators": {
                    "road_length_sanctioned": float(
                        row["Road Length Sanctioned"]
                    ),
                    "road_length_completed": float(
                        row["Road Length Completed"]
                    ),
                    "balance_road_length": float(
                        row["Balance Road Length"]
                    ),
                },
                "data_year": 2024,
                "source": "Karnataka OGD - PMGSY",
                "source_url": (
                    "https://karnataka.data.gov.in/"
                ),
            }
        )

    output_df = pd.DataFrame(records)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print(f"Processed records: {len(output_df)}")
    print(f"Saved: {OUTPUT_FILE}")

    print("\nSample:")
    print(
        output_df.head().to_string(index=False)
    )


if __name__ == "__main__":
    main()