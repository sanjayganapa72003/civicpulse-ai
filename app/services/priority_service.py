from app.services.demand_service import get_district_demand
from app.services.gap_service import calculate_gaps


DEMAND_WEIGHT = 0.35
SEVERITY_WEIGHT = 0.25
INFRASTRUCTURE_GAP_WEIGHT = 0.30
POPULATION_WEIGHT = 0.10


def normalize(
    value: float,
    minimum: float,
    maximum: float,
) -> float:

    if maximum == minimum:
        return 0.0

    return (value - minimum) / (maximum - minimum)


def build_priority_scores():

    demand = get_district_demand()
    gaps = calculate_gaps()

    max_demand = max(
        (
            data["total_requests"]
            for data in demand.values()
        ),
        default=1,
    )

    populations = []

    for district_data in gaps.values():

        demographics = district_data.get("demographics")

        if demographics and demographics.get("population") is not None:
            populations.append(
                demographics["population"]
            )

    max_population = max(
        populations,
        default=1,
    )

    priorities = []

    categories = [
        "road",
        "water",
        "healthcare",
    ]

    for district, district_demand in demand.items():

        district_gap = gaps.get(
            district,
            {},
        )

        infrastructure = district_gap.get(
            "infrastructure",
            {},
        )

        demographics = district_gap.get(
            "demographics"
        )

        population = (
            demographics.get("population")
            if demographics
            else None
        )

        population_score = (
            population / max_population
            if population is not None
            else 0.0
        )

        for category in categories:

            category_requests = district_demand.get(
                category,
                0,
            )

            if category_requests == 0:
                continue

            # -----------------------------------------
            # 1. CATEGORY-SPECIFIC DEMAND
            # -----------------------------------------

            category_demand_score = (
                category_requests / max_demand
            )

            # -----------------------------------------
            # 2. CATEGORY-SPECIFIC SEVERITY
            # -----------------------------------------

            severity_key = (
                f"{category}_average_severity"
            )

            category_average_severity = district_demand.get(
                severity_key,
                0.0,
            )

            severity_score = (
                category_average_severity / 5
            )

            # -----------------------------------------
            # 3. CATEGORY-SPECIFIC INFRASTRUCTURE GAP
            # -----------------------------------------

            infrastructure_gap_score = 0.0

            category_data = infrastructure.get(
                category
            )

            if category_data:

                gap = category_data.get(
                    "gap",
                    {},
                )

                if category == "water":

                    if gap.get("available"):
                        infrastructure_gap_score = gap.get(
                            "coverage_gap",
                            0.0,
                        )

                elif category == "road":

                    if gap.get("available"):

                        completion_ratio = gap.get(
                            "completion_ratio"
                        )

                        if completion_ratio is not None:
                            infrastructure_gap_score = (
                                1 - completion_ratio
                            )

                elif category == "healthcare":

                    # Healthcare gap is not benchmarked
                    # in the current MVP.
                    infrastructure_gap_score = 0.0

            # -----------------------------------------
            # 4. PRIORITY SCORE
            # -----------------------------------------

            priority_score = (
                category_demand_score
                * DEMAND_WEIGHT
                * 100
                +
                severity_score
                * SEVERITY_WEIGHT
                * 100
                +
                infrastructure_gap_score
                * INFRASTRUCTURE_GAP_WEIGHT
                * 100
                +
                population_score
                * POPULATION_WEIGHT
                * 100
            )

            priorities.append(
                {
                    "district": district,
                    "category": category,
                    "priority_score": round(
                        priority_score,
                        2,
                    ),
                    "signals": {
                        "demand_requests": category_requests,

                        "demand_score": round(
                            category_demand_score,
                            4,
                        ),

                        "average_severity": round(
                            category_average_severity,
                            2,
                        ),

                        "severity_score": round(
                            severity_score,
                            4,
                        ),

                        "infrastructure_gap_score": round(
                            infrastructure_gap_score,
                            4,
                        ),

                        "population": population,

                        "population_score": round(
                            population_score,
                            4,
                        ),
                    },
                }
            )

    priorities.sort(
        key=lambda item: item["priority_score"],
        reverse=True,
    )

    return priorities