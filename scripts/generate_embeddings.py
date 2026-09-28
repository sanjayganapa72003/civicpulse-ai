import json
import os
import time
from pathlib import Path

import voyageai
from dotenv import load_dotenv


load_dotenv()


INPUT_FILE = Path(
    "data/rag/processed/government_policy_chunks.jsonl"
)

OUTPUT_FILE = Path(
    "data/rag/processed/government_policy_embeddings.jsonl"
)

MODEL_NAME = "voyage-4-lite"
EMBEDDING_DIMENSION = 1024


def generate_embeddings():

    api_key = os.getenv("VOYAGE_API_KEY")

    if not api_key:
        raise RuntimeError(
            "VOYAGE_API_KEY is not set"
        )

    client = voyageai.Client(
        api_key=api_key
    )

    # -----------------------------------------------------
    # Load policy chunks
    # -----------------------------------------------------

    chunks = []

    with INPUT_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            chunks.append(
                json.loads(line)
            )

    print(
        f"Chunks loaded: {len(chunks)}"
    )

    # -----------------------------------------------------
    # Generate Voyage embeddings
    # -----------------------------------------------------

    print(
        f"Generating {MODEL_NAME} embeddings..."
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Voyage free-account limit:
    # 3 requests per minute.
    #
    # Small batches + delay keep us below
    # the rate limit.

    batch_size = 4

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        for start in range(
            0,
            len(chunks),
            batch_size,
        ):

            batch = chunks[
                start:start + batch_size
            ]

            texts = [
                chunk["text"]
                for chunk in batch
            ]

            result = client.embed(
                texts,
                model=MODEL_NAME,
                input_type="document",
                output_dimension=EMBEDDING_DIMENSION,
            )

            for chunk, embedding in zip(
                batch,
                result.embeddings,
            ):

                output = {
                    "chunk_id": chunk["chunk_id"],
                    "embedding": embedding,
                    "metadata": chunk["metadata"],
                }

                file.write(
                    json.dumps(
                        output,
                        ensure_ascii=False,
                    )
                    + "\n"
                )

            completed = min(
                start + batch_size,
                len(chunks),
            )

            print(
                f"Progress: "
                f"{completed}/{len(chunks)}"
            )

            # Don't sleep after the final request.
            if completed < len(chunks):
                time.sleep(21)

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    print()

    print("=" * 60)
    print("VOYAGE EMBEDDING GENERATION COMPLETED")
    print("=" * 60)

    print(
        f"Embeddings generated: "
        f"{len(chunks)}"
    )

    print(
        f"Embedding dimension: "
        f"{EMBEDDING_DIMENSION}"
    )

    print(
        f"Model: {MODEL_NAME}"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    generate_embeddings()