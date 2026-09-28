import sys
import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd


RAW_DIR = PROJECT_ROOT / "data" / "raw" / "healthcare"

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "healthcare.csv"
)


FILES = {
    "chc": "District_Wise_Public_Community_Health_Centres_in_Karnataka.csv",
    "phc": "District_Wise_Public_PrimaryHealthCenters_Non247_in_Karnataka.csv",
    "general_hospital": "District_Wise_Public_General_Hospitals_in_Karnataka_1.csv",
}


# Convert source-specific district names
# into the canonical district names used by CivicPulse.
DISTRICT_MAPPING = {
    "BAGALKOTE": "Bagalkot",
    "BALLARI": "Bellary",
    "BELAGAVI": "Belgaum",
    "BENGALURU RURAL": "Bangalore Rural",
    "BENGALURU URBAN": "Bangalore",
    "BBMP": "Bangalore",
    "CHAMARAJANAGARA": "Chamarajanagar",
    "CHIKKABALLAPURA": "Chikkaballapura",
    "CHIKKAMAGALURU": "Chikmagalur",
    "DAVANAGERE": "Davanagere",
    "KALABURAGI": "Gulbarga",
    "MYSURU": "Mysore",
    "SHIVAMOGGA": "Shimoga",
    "TUMAKURU": "Tumkur",
    "VIJAYAPURA": "Bijapur",
}


def normalize_district(name):
    """Convert a source district name to our canonical name."""

    name = str(name).strip().upper()

    return DISTRICT_MAPPING.get(
        name,
        name.title(),
    )


def load_facility_file(filename):
    """Load one healthcare facility dataset."""

    path = RAW_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"Healthcare file not found: {path}"
        )

    return pd.read_csv(path)


def count_by_district(df):
    """Count healthcare facilities by canonical district."""

    required_columns = [
        "DISTRICT_NAME",
        "Hospital",
        "TYPE_OF_FACILITY",
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

    counts = {}

    for district in df["DISTRICT_NAME"].dropna():

        canonical = normalize_district(district)

        counts[canonical] = (
            counts.get(canonical, 0) + 1
        )

    return counts


def main():

    print("Loading healthcare datasets...")

    # --------------------------------------------------
    # Load raw datasets
    # --------------------------------------------------

    chc_df = load_facility_file(
        FILES["chc"]
    )

    phc_df = load_facility_file(
        FILES["phc"]
    )

    hospital_df = load_facility_file(
        FILES["general_hospital"]
    )

    print(
        f"CHC facilities: {len(chc_df)}"
    )

    print(
        f"PHC facilities: {len(phc_df)}"
    )

    print(
        f"General hospitals: {len(hospital_df)}"
    )

    # --------------------------------------------------
    # Aggregate facilities by district
    # --------------------------------------------------

    chc_counts = count_by_district(
        chc_df
    )

    phc_counts = count_by_district(
        phc_df
    )

    hospital_counts = count_by_district(
        hospital_df
    )

    # Get every district appearing in at least
    # one of the three source datasets.
    districts = sorted(
        set(chc_counts)
        | set(phc_counts)
        | set(hospital_counts)
    )

    records = []

    # --------------------------------------------------
    # Build normalized healthcare records
    # --------------------------------------------------

    for district in districts:

        indicators = {}

        # Only include an indicator when the
        # corresponding source actually contains
        # records for this district.
        if district in chc_counts:
            indicators["chc_count"] = (
                chc_counts[district]
            )

        if district in phc_counts:
            indicators["phc_count"] = (
                phc_counts[district]
            )

        if district in hospital_counts:
            indicators["general_hospital_count"] = (
                hospital_counts[district]
            )

        records.append(
            {
                "state": "Karnataka",
                "district": district,
                "category": "healthcare",
                "indicators": indicators,
                "data_year": 2024,
                "source": (
                    "Karnataka OGD - "
                    "Health and Family Welfare Department"
                ),
                "source_url": (
                    "https://karnataka.data.gov.in/"
                ),
            }
        )

    # --------------------------------------------------
    # Save processed dataset
    # --------------------------------------------------

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
        f"\nProcessed districts: "
        f"{len(output_df)}"
    )

    print(
        f"Saved: {OUTPUT_FILE}"
    )

    print("\nSample:")

    print(
        output_df.head(10).to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()