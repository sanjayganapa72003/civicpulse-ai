import json
import os
from pathlib import Path

from dotenv import load_dotenv
from pinecone import Pinecone


load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

INDEX_NAME = "civicpulse-government-policies-voyage"

EMBEDDINGS_FILE = Path(
    "data/rag/processed/government_policy_embeddings.jsonl"
)

BATCH_SIZE = 50


def clean_metadata(metadata: dict) -> dict:
    return {
        key: value
        for key, value in metadata.items()
        if value is not None
    }


def upload_embeddings():

    if not PINECONE_API_KEY:
        raise ValueError(
            "PINECONE_API_KEY is not set"
        )

    pc = Pinecone(
        api_key=PINECONE_API_KEY
    )

    index = pc.Index(INDEX_NAME)

    vectors = []

    with EMBEDDINGS_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            item = json.loads(line)

            vectors.append(
                {
                    "id": item["chunk_id"],
                    "values": item["embedding"],
                    "metadata": clean_metadata(
                        item["metadata"]
                    ),
                }
            )

    print(
        f"Vectors loaded: {len(vectors)}"
    )

    # -----------------------------------------------------
    # Upload in batches
    # -----------------------------------------------------

    total_uploaded = 0

    for start in range(
        0,
        len(vectors),
        BATCH_SIZE,
    ):

        batch = vectors[
            start : start + BATCH_SIZE
        ]

        index.upsert(
            vectors=batch
        )

        total_uploaded += len(batch)

        print(
            f"Uploaded "
            f"{total_uploaded}/{len(vectors)} vectors"
        )

    print()
    print("=" * 60)
    print("PINECONE UPLOAD COMPLETED")
    print("=" * 60)

    print(
        f"Total vectors uploaded: "
        f"{total_uploaded}"
    )

    print(
        f"Index: {INDEX_NAME}"
    )


if __name__ == "__main__":
    upload_embeddings()