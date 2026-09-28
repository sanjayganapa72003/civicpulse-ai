import json
from pathlib import Path


INPUT_FILE = Path(
    "data/rag/processed/water_policy_chunks.jsonl"
)

OUTPUT_FILE = Path(
    "data/rag/processed/water_embedding_batch.jsonl"
)


def create_batch_file():
    count = 0

    with (
        INPUT_FILE.open("r", encoding="utf-8") as infile,
        OUTPUT_FILE.open("w", encoding="utf-8") as outfile,
    ):
        for line in infile:
            line = line.strip()

            if not line:
                continue

            chunk = json.loads(line)

            batch_request = {
                "key": chunk["chunk_id"],
                "request": {
                    "content": {
                        "parts": [
                            {
                                "text": chunk["text"]
                            }
                        ]
                    },
                    "embed_content_config": {
                        "task_type": "RETRIEVAL_DOCUMENT",
                        "output_dimensionality": 768
                    }
                }
            }

            outfile.write(
                json.dumps(
                    batch_request,
                    ensure_ascii=False
                ) + "\n"
            )

            count += 1

    print("Batch input created successfully")
    print(f"Chunks: {count}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    create_batch_file()