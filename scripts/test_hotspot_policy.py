import asyncio
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


from app.services.hotspot_policy_service import (
    generate_hotspot_policy_context,
)


async def main():
    district = "Bangalore"
    category = "water"

    result = await generate_hotspot_policy_context(
        district=district,
        category=category,
        top_k=5,
    )

    print("\n" + "=" * 80)
    print("HOTSPOT")
    print("=" * 80)

    print(f"District: {result['district']}")
    print(f"Category: {result['category']}")
    print(f"Found: {result['found']}")

    if not result["found"]:
        print(f"\n{result['message']}")
        return

    print("\n" + "=" * 80)
    print("HOTSPOT EVIDENCE")
    print("=" * 80)

    hotspot = result["hotspot"]

    print(f"Priority Score: {hotspot['priority_score']}")

    signals = hotspot["signals"]

    print(f"Citizen Requests: {signals['demand_requests']}")
    print(f"Average Severity: {signals['average_severity']}")
    print(
        f"Infrastructure Gap Score: "
        f"{signals['infrastructure_gap_score']}"
    )
    print(f"Population: {signals['population']}")

    print("\n" + "=" * 80)
    print("POLICY RETRIEVAL QUERY")
    print("=" * 80)

    print(result["policy_query"])

    print("\n" + "=" * 80)
    print("POLICY CONTEXT")
    print("=" * 80)

    policy_context = result["policy_context"]

    print("\nAnswer:")
    print(policy_context["answer"])

    print("\nEvidence:")

    for evidence in policy_context["evidence"]:
        print(
            f"- {evidence['document']} "
            f"(page {evidence['page']}): "
            f"{evidence['claim']}"
        )

    print("\nLimitations:")

    for limitation in policy_context["limitations"]:
        print(f"- {limitation}")


if __name__ == "__main__":
    asyncio.run(main())