import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd


RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "water"
    / "RS_Session_265_AU_99_A_to_B_i.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "water.csv"
)


def main():

    print("Loading water dataset...")

    df = pd.read_csv(RAW_FILE)

    print(f"Source records: {len(df)}")

    required_columns = [
        "Sl. No.",
        "District",
        "Number of PWS Village",
        "Total Number of households",
        "Number of Households with Household tap Connection",
        "Number of villages having 100% FHTC",
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

        district = str(
            row["District"]
        ).strip()

        total_households = int(
            row["Total Number of households"]
        )

        households_with_tap = int(
            row[
                "Number of Households with Household tap Connection"
            ]
        )

        pws_villages = int(
            row["Number of PWS Village"]
        )

        villages_100_fhtc = int(
            row[
                "Number of villages having 100% FHTC"
            ]
        )

        if total_households > 0:
            tap_coverage = (
                households_with_tap
                / total_households
            )
        else:
            tap_coverage = 0.0

        records.append(
            {
                "state": "Karnataka",
                "district": district,
                "category": "water",
                "indicators": {
                    "pws_villages": pws_villages,
                    "total_households": total_households,
                    "households_with_tap_connection": (
                        households_with_tap
                    ),
                    "villages_with_100_percent_fhtc": (
                        villages_100_fhtc
                    ),
                    "household_tap_coverage": (
                        round(tap_coverage, 4)
                    ),
                },
                "data_year": 2024,
                "source": "Karnataka OGD - Jal Jeevan Mission",
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

    print(
        f"Processed records: {len(output_df)}"
    )

    print(
        f"Saved: {OUTPUT_FILE}"
    )

    print("\nSample:")

    print(
        output_df.head().to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()