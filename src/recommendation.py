
import json
from pathlib import Path
from datetime import datetime, timezone


def build_recommendations(hypotheses, incident_id):
    """
    Convert investigation hypotheses into human-review
    recommendations. These are suggestions, not confirmed causes.
    """

    recommendations = []

    action_map = {
        "schedule": {
            "action": (
                "Review the building's operating schedule, "
                "occupancy records, and any after-hours activities "
                "during the incident."
            ),
            "priority": "High",
            "reason": (
                "The incident may be associated with an unusual "
                "operating schedule. Verify against facility records."
            )
        },
        "hvac": {
            "action": (
                "Review HVAC schedules, setpoints, runtime logs, "
                "and maintenance records for the incident period."
            ),
            "priority": "High",
            "reason": (
                "HVAC-related behavior is a plausible explanation, "
                "but supporting meter patterns alone do not prove it."
            )
        },
        "lighting": {
            "action": (
                "Inspect lighting and equipment schedules, "
                "after-hours usage, and relevant control logs."
            ),
            "priority": "Medium",
            "reason": (
                "Lighting or equipment operation may contribute "
                "to unusual consumption; verify before acting."
            )
        }
    }

    for hypothesis in hypotheses:
        # Accept either a hypothesis string or a dictionary.
        if isinstance(hypothesis, dict):
            name = str(
                hypothesis.get("hypothesis")
                or hypothesis.get("name")
                or hypothesis.get("title")
                or ""
            )
            evidence_level = hypothesis.get(
                "evidence_level",
                hypothesis.get("support_level", "Not specified")
            )
        else:
            name = str(hypothesis)
            evidence_level = "Not specified"

        text = name.lower()

        if "hvac" in text:
            category = "hvac"
        elif "lighting" in text or "equipment" in text:
            category = "lighting"
        elif "schedule" in text or "operation" in text:
            category = "schedule"
        else:
            continue

        template = action_map[category]

        recommendations.append({
            "incident_id": incident_id,
            "hypothesis": name,
            "evidence_level": evidence_level,
            "recommended_action": template["action"],
            "priority": template["priority"],
            "reason": template["reason"],
            "human_verification_required": True,
            "automated_control_performed": False
        })

    if not recommendations:
        recommendations.append({
            "incident_id": incident_id,
            "hypothesis": "Cause undetermined",
            "evidence_level": "Insufficient",
            "recommended_action": (
                "Review meter readings, facility schedules, "
                "and operational logs before deciding on corrective action."
            ),
            "priority": "Review",
            "reason": (
                "No matching evidence-supported hypothesis "
                "was available to generate a targeted recommendation."
            ),
            "human_verification_required": True,
            "automated_control_performed": False
        })

    return {
        "incident_id": incident_id,
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "recommendations": recommendations,
        "notice": (
            "Recommendations are decision-support suggestions. "
            "They do not establish causality and require human review."
        )
    }


if __name__ == "__main__":
    # Temporary integration test using the three
    # hypothesis categories from the investigation.
    # Later, connect this to actual evidence-scoring output.

    sample_hypotheses = [
        "Possible unusual building operating schedule",
        "Possible HVAC-related behavior",
        "Possible lighting or equipment operation"
    ]

    result = build_recommendations(
        sample_hypotheses,
        incident_id="INC-016"
    )

    output_path = Path("outputs/INC-016_recommendations.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print("Recommendation module executed.")
    print("Incident:", result["incident_id"])
    print("Recommendations:", len(result["recommendations"]))
    print("Saved to:", output_path)