
import json
from pathlib import Path
from datetime import datetime, timezone


def estimate_impact(historical_rows):
    """
    Estimate excess consumption using incident readings
    and their historical expected values.

    historical_rows: list of dictionaries containing
    actual and expected consumption values.
    """

    valid_rows = []

    for row in historical_rows:
        actual = row.get("actual")
        expected = row.get("expected")

        if actual is None or expected is None:
            continue

        try:
            actual = float(actual)
            expected = float(expected)
        except (TypeError, ValueError):
            continue

        if actual < 0 or expected < 0:
            continue

        valid_rows.append({
            "actual": actual,
            "expected": expected
        })

    if not valid_rows:
        return {
            "status": "INSUFFICIENT_DATA",
            "message": "No valid actual/expected pairs available."
        }

    total_actual = sum(r["actual"] for r in valid_rows)
    total_expected = sum(r["expected"] for r in valid_rows)

    # Only positive deviations count as potential excess.
    excess = sum(
        max(0, r["actual"] - r["expected"])
        for r in valid_rows
    )

    scenarios = {
        "10%": round(excess * 0.10, 2),
        "25%": round(excess * 0.25, 2),
        "50%": round(excess * 0.50, 2)
    }

    return {
        "status": "ESTIMATED",
        "observations_compared": len(valid_rows),
        "total_actual_consumption": round(total_actual, 2),
        "total_expected_consumption": round(total_expected, 2),
        "estimated_excess_consumption": round(excess, 2),
        "potential_reduction_scenarios": scenarios,
        "unit": "meter units; confirm dataset meter unit",
        "interpretation": (
            "Scenario estimates only. Excess consumption is not "
            "proof of avoidable waste or achievable savings."
        )
    }


def create_review_record(incident_id, impact, recommendations):
    """Create a human-review record and audit trail."""

    return {
        "incident_id": incident_id,
        "review_status": "PENDING_HUMAN_REVIEW",
        "reviewer_decision": None,
        "reviewer_name": None,
        "reviewer_notes": None,
        "impact_estimate": impact,
        "recommendations": recommendations,
        "automated_action_taken": False,
        "created_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "audit_events": [
            {
                "event": "IMPACT_ESTIMATED",
                "timestamp_utc": datetime.now(
                    timezone.utc
                ).isoformat()
            },
            {
                "event": "SENT_FOR_HUMAN_REVIEW",
                "timestamp_utc": datetime.now(
                    timezone.utc
                ).isoformat()
            }
        ]
    }


def save_review_record(record, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(record, file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    # Small test dataset to verify the calculation.
    # Replace with actual historical evidence during integration.

    sample_rows = [
        {"actual": 241, "expected": 178.5},
        {"actual": 183, "expected": 173},
        {"actual": 164, "expected": 154},
        {"actual": 147, "expected": 145}
    ]

    impact = estimate_impact(sample_rows)

    recommendations = [
        "Review building operating schedule and occupancy logs.",
        "Review HVAC runtime and maintenance records."
    ]

    record = create_review_record(
        incident_id="INC-016",
        impact=impact,
        recommendations=recommendations
    )

    save_review_record(
        record,
        "outputs/INC-016_review.json"
    )

    print("Impact estimation completed.")
    print("Estimated excess:",
          impact.get("estimated_excess_consumption"))
    print("Potential reduction scenarios:",
          impact.get("potential_reduction_scenarios"))
    print("Review status:", record["review_status"])
    print("Audit events:", len(record["audit_events"]))
    print("Saved to outputs/INC-016_review.json")