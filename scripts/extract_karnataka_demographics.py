import csv
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CENSUS_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "census"
    / "2011-IndiaStateDistSbDistVill-0000.xlsx"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "demographics.csv"
)

KARNATAKA_STATE_CODE = "29"
DATA_YEAR = 2011

SOURCE = "Census of India - PCA 2011"

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def load_shared_strings(zip_file):
    """Load Excel shared strings into a list."""

    shared_strings = []

    with zip_file.open("xl/sharedStrings.xml") as file:
        context = ET.iterparse(file, events=("end",))

        for event, elem in context:
            if elem.tag == f"{NS}si":
                text = "".join(
                    t.text or ""
                    for t in elem.iter(f"{NS}t")
                )
                shared_strings.append(text)

                elem.clear()

    return shared_strings


def get_cell_value(cell, shared_strings):
    """Extract the actual value from an Excel XML cell."""

    cell_type = cell.attrib.get("t")
    value_element = cell.find(f"{NS}v")

    if value_element is None:
        return ""

    value = value_element.text or ""

    if cell_type == "s":
        return shared_strings[int(value)]

    return value


def column_letter(cell_reference):
    """Extract column letters from a cell reference such as 'A12'."""

    return "".join(
        character
        for character in cell_reference
        if character.isalpha()
    )


def extract_karnataka_districts():
    """
    Extract Karnataka district-level Total/Rural/Urban
    population and household records from Census 2011.
    """

    records = {}

    with zipfile.ZipFile(CENSUS_FILE) as zip_file:

        print("Loading Excel shared strings...")
        shared_strings = load_shared_strings(zip_file)

        print("Streaming Census data...")

        with zip_file.open("xl/worksheets/sheet1.xml") as file:

            context = ET.iterparse(file, events=("end",))

            header = {}
            rows_processed = 0

            for event, elem in context:

                if elem.tag != f"{NS}row":
                    continue

                row = {}

                for cell in elem.findall(f"{NS}c"):

                    reference = cell.attrib.get("r")

                    if not reference:
                        continue

                    column = column_letter(reference)

                    row[column] = get_cell_value(
                        cell,
                        shared_strings,
                    )

                # First row contains column names
                if not header:
                    header = row
                    elem.clear()
                    continue

                rows_processed += 1

                level = row.get("G", "").strip()
                state_code = row.get("A", "").strip()

                # We only need Karnataka district-level records
                if (
                    level == "DISTRICT"
                    and state_code == KARNATAKA_STATE_CODE
                ):
                    district = row.get("H", "").strip()
                    tru = row.get("I", "").strip()

                    households = row.get("J", "").strip()
                    population = row.get("K", "").strip()

                    if not district or not tru:
                        elem.clear()
                        continue

                    record = {
                        "population": int(float(population)),
                        "households": int(float(households)),
                    }

                    records.setdefault(district, {})
                    records[district][tru] = record

                elem.clear()

    print(f"Total rows processed: {rows_processed:,}")
    print(f"Districts found: {len(records)}")

    return records


def transform_records(raw_records):
    """Convert Total/Rural/Urban records into our application schema."""

    demographics = []

    validation_errors = []

    for district, data in sorted(raw_records.items()):

        if not all(
            key in data
            for key in ["Total", "Rural", "Urban"]
        ):
            validation_errors.append(
                f"{district}: missing Total/Rural/Urban record"
            )
            continue

        total = data["Total"]
        rural = data["Rural"]
        urban = data["Urban"]

        # Validate population
        if total["population"] != (
            rural["population"] + urban["population"]
        ):
            validation_errors.append(
                f"{district}: population mismatch"
            )

        # Validate households
        if total["households"] != (
            rural["households"] + urban["households"]
        ):
            validation_errors.append(
                f"{district}: household mismatch"
            )

        demographics.append(
            {
                "state": "Karnataka",
                "district": district,
                "population": total["population"],
                "rural_population": rural["population"],
                "urban_population": urban["population"],
                "households": total["households"],
                "data_year": DATA_YEAR,
                "source": SOURCE,
            }
        )

    if validation_errors:
        print("\nValidation errors:")

        for error in validation_errors:
            print(f"  - {error}")

        raise ValueError(
            f"Found {len(validation_errors)} validation errors."
        )

    return demographics


def save_csv(records):
    """Save normalized demographic records to CSV."""

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "state",
        "district",
        "population",
        "rural_population",
        "urban_population",
        "households",
        "data_year",
        "source",
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
        writer.writerows(records)

    print(f"\nSaved CSV:")
    print(OUTPUT_FILE)


def print_summary(records):
    """Print a concise validation summary."""

    print("\n" + "=" * 60)
    print("KARNATAKA DEMOGRAPHICS SUMMARY")
    print("=" * 60)

    print(f"District records : {len(records)}")

    total_population = sum(
        record["population"]
        for record in records
    )

    total_households = sum(
        record["households"]
        for record in records
    )

    print(f"Total population : {total_population:,}")
    print(f"Total households : {total_households:,}")

    print("\nSample records:")

    for record in records[:5]:
        print(
            f"  {record['district']}: "
            f"population={record['population']:,}, "
            f"rural={record['rural_population']:,}, "
            f"urban={record['urban_population']:,}, "
            f"households={record['households']:,}"
        )

    print("=" * 60)


def main():

    if not CENSUS_FILE.exists():
        raise FileNotFoundError(
            f"Census file not found:\n{CENSUS_FILE}"
        )

    raw_records = extract_karnataka_districts()

    records = transform_records(raw_records)

    # For the 2011 Karnataka source, we expect
    # 30 district-level records.
    if len(records) != 30:
        raise ValueError(
            f"Expected 30 district records, "
            f"but found {len(records)}."
        )

    save_csv(records)

    print_summary(records)


if __name__ == "__main__":
    main()