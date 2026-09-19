
import json
from pathlib import Path

from src.recommendation import build_recommendations
from src.impact import estimate_impact, create_review_record


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def normalize_hypotheses(raw_hypotheses):
    """
    Convert evidence-assessment hypotheses into the format
    expected by recommendation.py.

    Source field: evidence_quality
    Output field: evidence_level
    """

    normalized = []

    for item in raw_hypotheses:
        if not isinstance(item, dict):
            continue

        name = (
            item.get("hypothesis")
            or item.get("name")
            or item.get("title")
        )

        evidence_level = (
            item.get("evidence_quality")
            or item.get("evidence_level")
            or item.get("support_level")
            or "Not specified"
        )

        if name:
            normalized.append({
                "hypothesis": str(name),
                "evidence_level": str(evidence_level)
            })

    return normalized


def run_pipeline(incident_id="INC-016"):

    # Load investigation artifact.
    investigation_path = (
        OUTPUTS / f"{incident_id}_investigation.json"
    )

    if not investigation_path.exists():
        raise FileNotFoundError(
            f"Investigation output not found: {investigation_path}"
        )

    investigation = load_json(investigation_path)

    # 1. Calculate impact from historical evidence.
    historical = investigation.get("historical_evidence", [])

    impact_rows = [
        {
            "actual": row.get("actual_electricity"),
            "expected": row.get("historical_expected")
        }
        for row in historical
    ]

    impact = estimate_impact(impact_rows)

    # 2. Extract hypotheses from the correct source structure.
    assessment = investigation.get("evidence_assessment", {})
    raw_hypotheses = assessment.get("hypotheses", [])

    hypotheses = normalize_hypotheses(raw_hypotheses)

    # Stop instead of silently generating unsupported recommendations.
    if not hypotheses:
        raise ValueError(
            "No valid hypotheses found in "
            "evidence_assessment.hypotheses. "
            "Check the investigation JSON."
        )

    # 3. Generate recommendations with preserved evidence levels.
    recommendation_result = build_recommendations(
        hypotheses,
        incident_id
    )

    recommendations = recommendation_result.get(
        "recommendations", []
    )

    # 4. Create human-review record.
    record = create_review_record(
        incident_id=incident_id,
        impact=impact,
        recommendations=recommendations
    )

    record["building_id"] = investigation.get("building_id")
    record["investigation_status"] = investigation.get(
        "investigation_status"
    )
    record["tools_used"] = investigation.get("tools_used", [])

    # 5. Save integrated artifact.
    output_path = OUTPUTS / f"{incident_id}_integrated.json"

    save_json(output_path, record)

    # 6. Print pipeline summary.
    print("Integrated pipeline completed.")
    print("Incident:", incident_id)
    print("Historical rows used:", len(historical))

    print(
        "Estimated excess:",
        impact.get("estimated_excess_consumption", "N/A")
    )

    print("Recommendations:", len(recommendations))

    print("Evidence levels:", [
        r.get("evidence_level") for r in recommendations
    ])

    print("Review status:", record["review_status"])
    print("Saved to:", output_path)


if __name__ == "__main__":
    run_pipeline("INC-016")