import json
from pathlib import Path

from sentence_transformers import SentenceTransformer


INPUT_FILE = Path(
    "data/rag/processed/government_policy_chunks.jsonl"
)

OUTPUT_FILE = Path(
    "data/rag/processed/government_policy_embeddings.jsonl"
)

MODEL_NAME = "intfloat/multilingual-e5-base"


def generate_embeddings():

    print(f"Loading model: {MODEL_NAME}")

    model = SentenceTransformer(
        MODEL_NAME
    )

    # -----------------------------------------------------
    # Load unified government-policy corpus
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
    # Prepare passages for E5
    # -----------------------------------------------------

    passages = [
        f"passage: {chunk['text']}"
        for chunk in chunks
    ]

    print(
        "Generating embeddings..."
    )

    embeddings = model.encode(
        passages,
        batch_size=8,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    # -----------------------------------------------------
    # Save embeddings
    # -----------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        "Saving embeddings..."
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        for chunk, embedding in zip(
            chunks,
            embeddings,
        ):

            output = {
                "chunk_id": chunk["chunk_id"],
                "embedding": embedding.tolist(),
                "metadata": chunk["metadata"],
            }

            file.write(
                json.dumps(
                    output,
                    ensure_ascii=False,
                )
                + "\n"
            )

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    print()
    print("=" * 60)
    print("EMBEDDING GENERATION COMPLETED")
    print("=" * 60)

    print(
        f"Embeddings generated: {len(embeddings)}"
    )

    print(
        f"Embedding dimension: "
        f"{len(embeddings[0])}"
    )

    print(
        f"Output: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    generate_embeddings()