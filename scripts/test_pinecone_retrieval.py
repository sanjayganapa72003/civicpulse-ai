import os

from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer


load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

INDEX_NAME = "civicpulse-water-policies"
MODEL_NAME = "intfloat/multilingual-e5-base"


def main():
    # Load embedding model
    print(f"Loading model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    # Connect to Pinecone
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(INDEX_NAME)

    # Test query
    query = "What government guidelines address low household tap water coverage?"

    print(f"\nQuery:")
    print(query)

    # E5 requires the query prefix
    query_embedding = model.encode(
        f"query: {query}",
        normalize_embeddings=True,
    ).tolist()

    print(f"\nQuery embedding dimension: {len(query_embedding)}")

    # Search Pinecone
    results = index.query(
        vector=query_embedding,
        top_k=5,
        include_metadata=True,
    )

    print("\nTop results:\n")

    for i, match in enumerate(results["matches"], start=1):
        metadata = match.get("metadata", {})

        print("=" * 70)
        print(f"Result #{i}")
        print(f"Score: {match['score']}")
        print(f"Chunk ID: {match['id']}")
        print(f"Title: {metadata.get('title')}")
        print(f"Page: {metadata.get('page')}")
        print(f"Section: {metadata.get('section')}")
        print(f"Document type: {metadata.get('document_type')}")
        print(f"Source: {metadata.get('source')}")


if __name__ == "__main__":
    main()