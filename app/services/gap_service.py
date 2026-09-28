from app.services.demand_service import get_district_demand
from app.services.infrastructure_service import get_district_infrastructure


def calculate_water_gap(indicators: dict) -> dict:
    coverage = indicators.get("household_tap_coverage")

    if coverage is None:
        return {
            "available": False,
            "reason": "Household tap coverage data unavailable",
        }

    return {
        "available": True,
        "household_tap_coverage": coverage,
        "coverage_gap": round(1 - coverage, 4),
    }


def calculate_road_gap(indicators: dict) -> dict:
    sanctioned = indicators.get("road_length_sanctioned")
    completed = indicators.get("road_length_completed")
    balance = indicators.get("balance_road_length")

    if sanctioned is None or completed is None:
        return {
            "available": False,
            "reason": "Road completion data unavailable",
        }

    completion_ratio = completed / sanctioned if sanctioned > 0 else None

    return {
        "available": True,
        "road_length_sanctioned": sanctioned,
        "road_length_completed": completed,
        "balance_road_length": balance,
        "completion_ratio": (
            round(completion_ratio, 4)
            if completion_ratio is not None
            else None
        ),
    }


def calculate_healthcare_gap(indicators: dict) -> dict:
    result = {
        "available": True,
        "facility_counts": {},
        "gap_assessment": None,
    }

    for key in (
        "chc_count",
        "phc_count",
        "general_hospital_count",
    ):
        if key in indicators:
            result["facility_counts"][key] = indicators[key]

    if not result["facility_counts"]:
        result["available"] = False
        result["reason"] = "Healthcare facility data unavailable"

    return result


def calculate_gaps():
    demand = get_district_demand()
    infrastructure = get_district_infrastructure()

    result = {}

    all_districts = set(demand.keys()) | set(infrastructure.keys())

    for district in all_districts:
        district_demand = demand.get(
            district,
            {
                "total_requests": 0,
                "road": 0,
                "water": 0,
                "healthcare": 0,
                "average_severity": None,
            },
        )

        district_infrastructure = infrastructure.get(
            district,
            {
                "infrastructure": {},
                "demographics": None,
            },
        )

        infrastructure_data = district_infrastructure.get(
            "infrastructure", {}
        )

        district_result = {
            "demand": district_demand,
            "infrastructure": {},
            "demographics": district_infrastructure.get("demographics"),
        }

        # Road gap
        if "road" in infrastructure_data:
            district_result["infrastructure"]["road"] = {
                "demand_requests": district_demand["road"],
                "gap": calculate_road_gap(
                    infrastructure_data["road"]["indicators"]
                ),
            }

        # Water gap
        if "water" in infrastructure_data:
            district_result["infrastructure"]["water"] = {
                "demand_requests": district_demand["water"],
                "gap": calculate_water_gap(
                    infrastructure_data["water"]["indicators"]
                ),
            }

        # Healthcare indicators
        if "healthcare" in infrastructure_data:
            district_result["infrastructure"]["healthcare"] = {
                "demand_requests": district_demand["healthcare"],
                "gap": calculate_healthcare_gap(
                    infrastructure_data["healthcare"]["indicators"]
                ),
            }

        result[district] = district_result

    return result