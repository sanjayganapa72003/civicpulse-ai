import asyncio
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


from app.services.rag_generation_service import generate_policy_answer


async def main():
    query = (
        "What government policy context is relevant when a district "
        "has low household tap water coverage?"
    )

    result = await generate_policy_answer(
        query=query,
        top_k=5,
    )

    print("\nQuery:")
    print(query)

    print("\nAnswer:")
    print(result["answer"])

    print("\nEvidence:")

    for evidence in result["evidence"]:
        print(
            f"- {evidence['document']} "
            f"(page {evidence['page']}): "
            f"{evidence['claim']}"
        )

    print("\nLimitations:")

    for limitation in result["limitations"]:
        print(f"- {limitation}")


if __name__ == "__main__":
    asyncio.run(main())