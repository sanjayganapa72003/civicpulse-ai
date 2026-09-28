from app.services.priority_service import build_priority_scores


def get_hotspots(limit: int = 10):
    priorities = build_priority_scores()

    hotspots = []

    for item in priorities[:limit]:
        hotspots.append(
            {
                "district": item["district"],
                "category": item["category"],
                "priority_score": item["priority_score"],
                "signals": item["signals"],
            }
        )

    return {
        "total_hotspots": len(hotspots),
        "hotspots": hotspots,
    }