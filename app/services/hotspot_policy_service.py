from typing import Any

from app.db.mongodb import db
from app.services.gap_service import calculate_gaps
from app.services.priority_service import build_priority_scores
from app.services.rag_retrieval_service import retrieve_policy_chunks


citizen_requests_collection = db["citizen_requests"]


def get_dominant_issue_type(
    district: str,
    category: str,
) -> str | None:
    """
    Find the most frequently reported issue type
    for a district/category combination.
    """

    pipeline = [
        {
            "$match": {
                "district": district,
                "category": category,
            }
        },
        {
            "$group": {
                "_id": "$issue_type",
                "count": {"$sum": 1},
            }
        },
        {
            "$sort": {
                "count": -1,
            }
        },
        {
            "$limit": 1,
        },
    ]

    result = list(
        citizen_requests_collection.aggregate(pipeline)
    )

    if not result:
        return None

    return result[0]["_id"]


def build_gap_description(
    category: str,
    gap_data: dict[str, Any],
) -> str:

    if category == "water":
        gap = gap_data.get("gap", {})

        if gap.get("available"):
            return (
                "household drinking-water access has an "
                "infrastructure coverage gap"
            )

        return "household drinking-water coverage data is unavailable"

    if category == "road":
        gap = gap_data.get("gap", {})

        if gap.get("available"):
            return (
                "road connectivity has an incomplete "
                "infrastructure delivery gap"
            )

        return "road completion data is unavailable"

    if category == "healthcare":
        facility_counts = gap_data.get(
            "gap",
            {},
        ).get(
            "facility_counts",
            {},
        )

        if facility_counts:
            return (
                "healthcare service accessibility and "
                "facility availability"
            )

        return "healthcare facility availability data is unavailable"

    return "infrastructure gap information is unavailable"


def build_policy_retrieval_query(
    category: str,
    issue_type: str,
    gap_description: str,
) -> str:
    """
    Build a semantic query for the government-policy corpus.

    This query describes the development problem rather than
    asking Pinecone to search for internal metric names.
    """

    return (
        f"{category} infrastructure: "
        f"{issue_type} and {gap_description}. "
        "Find Indian government policies, guidelines, "
        "programmes, implementation frameworks, and "
        "service standards related to this problem."
    )


def get_hotspot_policy_context(
    district: str,
    category: str,
    top_k: int = 5,
) -> dict[str, Any]:
    """
    Retrieve government policy evidence for a hotspot.
    """

    priorities = build_priority_scores()
    gaps = calculate_gaps()

    hotspot = None

    for item in priorities:
        if (
            item["district"] == district
            and item["category"] == category
        ):
            hotspot = item
            break

    if hotspot is None:
        return {
            "available": False,
            "reason": (
                f"No priority record found for "
                f"{district} / {category}"
            ),
        }

    district_gap = gaps.get(district, {})

    infrastructure = district_gap.get(
        "infrastructure",
        {},
    )

    category_gap = infrastructure.get(
        category,
        {},
    )

    issue_type = get_dominant_issue_type(
        district,
        category,
    )

    if not issue_type:
        issue_type = f"{category} infrastructure need"

    gap_description = build_gap_description(
        category,
        category_gap,
    )

    retrieval_query = build_policy_retrieval_query(
        category=category,
        issue_type=issue_type,
        gap_description=gap_description,
    )

    policy_chunks = retrieve_policy_chunks(
        query=retrieval_query,
        top_k=top_k,
    )

    return {
        "available": True,
        "district": district,
        "category": category,
        "issue_type": issue_type,
        "gap_description": gap_description,
        "retrieval_query": retrieval_query,
        "priority": hotspot,
        "policy_chunks": policy_chunks,
    }