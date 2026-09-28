import os

from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer


load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

INDEX_NAME = "civicpulse-government-policies"
MODEL_NAME = "intfloat/multilingual-e5-base"


model = SentenceTransformer(MODEL_NAME)

pc = Pinecone(
    api_key=PINECONE_API_KEY
)

index = pc.Index(INDEX_NAME)


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


def search(query: str, top_k: int = 5):

    query_embedding = model.encode(
        f"query: {query}",
        normalize_embeddings=True,
    ).tolist()

    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
    )

    return results.get("matches", [])


def main():

    for domain, query in TEST_QUERIES.items():

        print()
        print("=" * 80)
        print(f"DOMAIN: {domain.upper()}")
        print(f"QUERY: {query}")
        print("=" * 80)

        matches = search(query)

        for rank, match in enumerate(
            matches,
            start=1,
        ):

            metadata = match.get(
                "metadata",
                {},
            )

            print()
            print(f"#{rank}")
            print(
                f"Score: {match['score']:.4f}"
            )
            print(
                f"Domain: "
                f"{metadata.get('domain')}"
            )
            print(
                f"Document: "
                f"{metadata.get('title')}"
            )
            print(
                f"Page: "
                f"{metadata.get('page')}"
            )


if __name__ == "__main__":
    main()