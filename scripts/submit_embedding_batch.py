import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

INPUT_FILE = (
    "data/rag/processed/water_embedding_batch.jsonl"
)

MODEL = "gemini-embedding-001"


def main():
    print("Uploading batch input file...")

    uploaded_file = client.files.upload(
        file=INPUT_FILE,
        config=types.UploadFileConfig(
            display_name="water-policy-embedding-batch",
            mime_type="jsonl",
        ),
    )

    print("File uploaded successfully")
    print(f"File name: {uploaded_file.name}")

    print("\nCreating embedding batch job...")

    batch_job = client.batches.create_embeddings(
        model=MODEL,
        src={
            "file_name": uploaded_file.name
        },
        config={
            "display_name": "CivicPulse Water Policy Embeddings"
        },
    )

    print("\nBatch job created successfully")
    print(f"Job name: {batch_job.name}")
    print(f"State: {batch_job.state}")


if __name__ == "__main__":
    main()