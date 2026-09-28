import os

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec


load_dotenv()

PINECONE_API_KEY = os.getenv(
    "PINECONE_API_KEY"
)

INDEX_NAME = "civicpulse-government-policies"

DIMENSION = 768
METRIC = "cosine"

CLOUD = "aws"
REGION = "us-east-1"


def create_index():

    if not PINECONE_API_KEY:
        raise ValueError(
            "PINECONE_API_KEY is not set"
        )

    pc = Pinecone(
        api_key=PINECONE_API_KEY
    )

    existing_indexes = [
        index["name"]
        for index in pc.list_indexes()
    ]

    if INDEX_NAME in existing_indexes:

        print(
            f"Index already exists: {INDEX_NAME}"
        )

        return

    print(
        f"Creating index: {INDEX_NAME}"
    )

    pc.create_index(
        name=INDEX_NAME,
        dimension=DIMENSION,
        metric=METRIC,
        spec=ServerlessSpec(
            cloud=CLOUD,
            region=REGION,
        ),
    )

    print(
        f"Index created successfully: "
        f"{INDEX_NAME}"
    )


if __name__ == "__main__":
    create_index()