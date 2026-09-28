import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
from app.services.rag_retrieval_service import retrieve_policy_chunks


def main():
    query = "What government guidelines address low household tap water coverage?"

    results = retrieve_policy_chunks(
        query=query,
        top_k=5,
    )

    print(f"\nQuery: {query}")
    print(f"Retrieved chunks: {len(results)}\n")

    for i, result in enumerate(results, start=1):
        print("=" * 80)
        print(f"Result #{i}")
        print(f"Score: {result['score']:.4f}")
        print(f"Chunk ID: {result['chunk_id']}")
        print(f"Title: {result['title']}")
        print(f"Page: {result['page']}")
        print(f"Section: {result['section']}")
        print(f"Source: {result['source']}")

        print("\nTEXT:")
        print(result["text"][:1000])


if __name__ == "__main__":
    main()