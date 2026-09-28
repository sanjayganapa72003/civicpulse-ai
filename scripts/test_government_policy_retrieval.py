import os

from dotenv import load_dotenv
from pinecone import Pinecone
import voyageai
import time

load_dotenv()


PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")

INDEX_NAME = "civicpulse-government-policies-voyage"
MODEL_NAME = "voyage-4-lite"
EMBEDDING_DIMENSION = 1024


voyage_client = voyageai.Client(
    api_key=VOYAGE_API_KEY
)

pc = Pinecone(
    api_key=PINECONE_API_KEY
)

index = pc.Index(
    INDEX_NAME
)


TEST_QUERIES = {
    "water": (
        "government guidelines for "
        "low household tap water coverage"
    ),
    "roads": (
        "government guidelines for "
        "rural road connectivity and road completion"
    ),
    "healthcare": (
        "government standards for "
        "public healthcare facilities and primary healthcare"
    ),
    "investment": (
        "government framework for infrastructure "
        "planning and identifying infrastructure gaps"
    ),
}


def search(
    query: str,
    top_k: int = 5,
):

    response = voyage_client.embed(
        [query],
        model=MODEL_NAME,
        input_type="query",
        output_dimension=EMBEDDING_DIMENSION,
    )

    query_embedding = response.embeddings[0]

    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
    )

    return results.get(
        "matches",
        []
    )


def main():
    for index, (domain, query) in enumerate(TEST_QUERIES.items()):

        if index > 0:
            print("\nWaiting 21 seconds for Voyage rate limit...")
            time.sleep(21)

        print()
        print("=" * 80)
        print(f"DOMAIN: {domain.upper()}")
        print(f"QUERY: {query}")
        print("=" * 80)

        matches = search(query)

        for rank, match in enumerate(matches, start=1):
            metadata = match.get("metadata", {})

            print()
            print(f"#{rank}")
            print(f"Score: {match['score']:.4f}")
            print(f"Domain: {metadata.get('domain')}")
            print(f"Document: {metadata.get('title')}")
            print(f"Page: {metadata.get('page')}")


if __name__ == "__main__":
    main()