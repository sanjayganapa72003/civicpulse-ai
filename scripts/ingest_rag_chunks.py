from pathlib import Path
import json
import sys

from pymongo import ASCENDING

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.db.mongodb import db


INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "rag"
    / "processed"
    / "government_policy_chunks.jsonl"
)

COLLECTION_NAME = "rag_chunks"


def ingest_rag_chunks():
    collection = db[COLLECTION_NAME]

    # Remove the previous water-only corpus
    collection.delete_many({})

    documents = []

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            chunk = json.loads(line)

            documents.append({
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "metadata": chunk["metadata"],
            })

    if not documents:
        print("No chunks found.")
        return

    collection.insert_many(documents, ordered=False)

    collection.create_index(
        [("chunk_id", ASCENDING)],
        unique=True,
    )

    print(f"RAG chunks ingested: {len(documents)}")
    print(f"MongoDB collection: {COLLECTION_NAME}")


if __name__ == "__main__":
    ingest_rag_chunks()