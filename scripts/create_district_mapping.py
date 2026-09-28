import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "district_mapping.csv"
)


MAPPINGS = [
    # Census / Road naming differences
    {
        "source": "roads",
        "source_district": "Bangalore R",
        "canonical_district": "Bangalore Rural",
    },
    {
        "source": "roads",
        "source_district": "Bangalore U",
        "canonical_district": "Bangalore",
    },
    {
        "source": "roads",
        "source_district": "Chickballapur",
        "canonical_district": "Chikkaballapura",
    },
    {
        "source": "roads",
        "source_district": "Chickmagalur",
        "canonical_district": "Chikmagalur",
    },
    {
        "source": "roads",
        "source_district": "Ramnagar",
        "canonical_district": "Ramanagara",
    },
]


def main():

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "source",
        "source_district",
        "canonical_district",
    ]

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(MAPPINGS)

    print(
        f"Saved {len(MAPPINGS)} mappings to:"
    )
    print(OUTPUT_FILE)

    print("\nMappings:")

    for mapping in MAPPINGS:
        print(
            f"  {mapping['source_district']}"
            f" -> "
            f"{mapping['canonical_district']}"
        )


if __name__ == "__main__":
    main()