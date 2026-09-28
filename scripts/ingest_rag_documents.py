import re
import sys
import unicodedata
from pathlib import Path

import fitz
import pytesseract
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAG_DIR = PROJECT_ROOT / "data" / "rag"
OUTPUT_DIR = RAG_DIR / "processed"

OUTPUT_FILE = OUTPUT_DIR / "government_policy_chunks.jsonl"

TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

CHUNK_SIZE = 3500
CHUNK_OVERLAP = 400

MIN_CHUNK_LENGTH = 300

SUPPORTED_DOMAINS = {
    "water",
    "roads",
    "healthcare",
    "investment",
}


# ---------------------------------------------------------
# Text cleaning
# ---------------------------------------------------------

def clean_text(text: str) -> str:
    """
    Clean OCR/PDF extraction artifacts while preserving
    meaningful policy text.
    """

    text = unicodedata.normalize("NFKC", text)

    # Remove unusual control characters
    text = "".join(
        char
        for char in text
        if char.isprintable() or char in "\n\t"
    )

    # Replace common OCR artifacts
    replacements = {
        "\u00ad": "",
        "\ufb00": "ff",
        "\ufb01": "fi",
        "\ufb02": "fl",
        "\ufb03": "ffi",
        "\ufb04": "ffl",
        "\ufb05": "st",
        "\ufb06": "st",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Normalize whitespace
    text = re.sub(r"[ \t]+", " ", text)

    # Reduce excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ---------------------------------------------------------
# OCR
# ---------------------------------------------------------

def extract_page_text(page) -> tuple[str, str]:
    """
    Try normal PDF text extraction first.

    If insufficient text is available, render the page
    and use Tesseract OCR.
    """

    text = page.get_text("text").strip()

    # Normal PDF text is usually preferable.
    if len(text) >= 100:
        return clean_text(text), "pdf_text"

    # OCR fallback
    pix = page.get_pixmap(
        dpi=300,
        alpha=False,
    )

    image = Image.frombytes(
        "RGB",
        [pix.width, pix.height],
        pix.samples,
    )

    ocr_text = pytesseract.image_to_string(
        image,
        lang="eng",
    )

    return clean_text(ocr_text), "ocr"


# ---------------------------------------------------------
# Document metadata
# ---------------------------------------------------------

def get_document_metadata(
    pdf_path: Path,
) -> dict:

    domain = pdf_path.parent.name

    if domain not in SUPPORTED_DOMAINS:
        raise ValueError(
            f"Unsupported RAG domain: {domain}"
        )

    filename = pdf_path.name

    metadata = {
        "domain": domain,
        "document_id": pdf_path.stem,
        "title": pdf_path.stem.replace("_", " "),
        "document_type": "government_guideline",
        "language": "english",
        "year": None,
        "source": "Government of India",
        "extraction_method": None,
    }

    # Known document years
    if "2022" in filename:
        metadata["year"] = 2022

    elif "jjm_2_0" in filename:
        metadata["year"] = 2026

    elif "drinking_water_quality" in filename:
        metadata["year"] = 2021

    elif "pmgsy_iii" in filename:
        metadata["year"] = 2019

    elif "gatishakti" in filename:
        metadata["year"] = 2022

    return metadata


# ---------------------------------------------------------
# Chunking
# ---------------------------------------------------------

def create_chunks(
    text: str,
) -> list[str]:

    if not text:
        return []

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = min(
            start + CHUNK_SIZE,
            text_length,
        )

        chunk = text[start:end].strip()

        if len(chunk) >= MIN_CHUNK_LENGTH:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - CHUNK_OVERLAP

    return chunks


# ---------------------------------------------------------
# Quality filtering
# ---------------------------------------------------------

def is_quality_chunk(text: str) -> bool:

    if len(text) < MIN_CHUNK_LENGTH:
        return False

    alphanumeric_count = sum(
        char.isalnum()
        for char in text
    )

    if alphanumeric_count == 0:
        return False

    alphanumeric_ratio = (
        alphanumeric_count / len(text)
    )

    # Reject heavily corrupted OCR
    if alphanumeric_ratio < 0.35:
        return False

    return True


# ---------------------------------------------------------
# Process one PDF
# ---------------------------------------------------------

def process_document(
    pdf_path: Path,
) -> list[dict]:

    print()
    print("=" * 70)
    print(f"Processing: {pdf_path.name}")
    print(f"Domain: {pdf_path.parent.name}")
    print("=" * 70)

    metadata = get_document_metadata(pdf_path)

    document = fitz.open(pdf_path)

    chunks = []

    for page_number, page in enumerate(
        document,
        start=1,
    ):

        text, extraction_method = extract_page_text(
            page
        )

        if not text:
            continue

        page_chunks = create_chunks(text)

        for chunk_index, chunk_text in enumerate(
            page_chunks
        ):

            if not is_quality_chunk(chunk_text):
                continue

            chunk_id = (
                f"{metadata['document_id']}"
                f"_p{page_number}"
                f"_c{chunk_index}"
            )

            chunk_metadata = {
                **metadata,
                "page": page_number,
                "extraction_method": extraction_method,
            }

            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "text": chunk_text,
                    "metadata": chunk_metadata,
                }
            )

    document.close()

    print(
        f"Quality chunks generated: {len(chunks)}"
    )

    return chunks


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    all_chunks = []

    for domain in sorted(SUPPORTED_DOMAINS):

        domain_dir = RAG_DIR / domain

        if not domain_dir.exists():
            print(
                f"Skipping missing directory: {domain_dir}"
            )
            continue

        pdf_files = sorted(
            domain_dir.glob("*.pdf")
        )

        print()
        print(
            f"{domain.upper()}: "
            f"{len(pdf_files)} PDF(s)"
        )

        for pdf_path in pdf_files:

            chunks = process_document(
                pdf_path
            )

            all_chunks.extend(chunks)

    # -----------------------------------------------------
    # Write unified corpus
    # -----------------------------------------------------

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        for chunk in all_chunks:
            import json

            file.write(
                json.dumps(
                    chunk,
                    ensure_ascii=False,
                )
                + "\n"
            )

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    domain_counts = {}

    for chunk in all_chunks:

        domain = chunk["metadata"]["domain"]

        domain_counts[domain] = (
            domain_counts.get(domain, 0) + 1
        )

    print()
    print("=" * 70)
    print("RAG INGESTION COMPLETED")
    print("=" * 70)

    print(
        f"Total quality chunks: {len(all_chunks)}"
    )

    for domain, count in sorted(
        domain_counts.items()
    ):
        print(
            f"{domain}: {count} chunks"
        )

    print(
        f"Output: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()