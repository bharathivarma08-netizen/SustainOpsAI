from pathlib import Path
import sys
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from anomaly_detector import (
    load_electricity_data,
    add_time_features,
    calculate_robust_baseline,
    calculate_anomaly_score,
)

BUILDING_ID = "Eagle_education_Wesley"


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

CANDIDATE_QUANTILE = 0.99

# Maximum time gap allowed between candidate anomalies
# before they are considered part of the same incident.
MAX_GAP_HOURS = 24


# ---------------------------------------------------------
# CREATE CANDIDATE ANOMALIES
# ---------------------------------------------------------

def get_candidate_anomalies(data):
    """
    Identify high-consumption candidate anomalies using
    the upper quantile of positive robust anomaly scores.
    """

    high = data[
        (data["direction"] == "HIGH") &
        (data["robust_score"].notna())
    ].copy()

    threshold = high["robust_score"].quantile(CANDIDATE_QUANTILE)

    candidates = high[
        high["robust_score"] >= threshold
    ].copy()

    candidates = candidates.sort_values("timestamp").reset_index(drop=True)

    return candidates, threshold


# ---------------------------------------------------------
# FORM INCIDENTS
# ---------------------------------------------------------

def form_incidents(candidates):
    """
    Group candidate anomalies into incidents based on
    the temporal gap between consecutive candidates.
    """

    candidates = candidates.copy()

    if candidates.empty:
        return candidates, []

    candidates["gap_hours"] = (
        candidates["timestamp"]
        .diff()
        .dt.total_seconds()
        / 3600
    )

    # A new incident starts when:
    # 1. It is the first candidate, or
    # 2. The gap exceeds MAX_GAP_HOURS

    candidates["new_incident"] = (
        candidates["gap_hours"].isna()
        | (candidates["gap_hours"] > MAX_GAP_HOURS)
    )

    candidates["incident_number"] = (
        candidates["new_incident"]
        .cumsum()
    )

    incidents = []

    for incident_number, group in candidates.groupby(
        "incident_number"
    ):

        incident = {
            "incident_id": f"INC-{incident_number:03d}",
            "start": group["timestamp"].min(),
            "end": group["timestamp"].max(),
            "candidate_count": len(group),
            "max_relative_deviation": group[
                "relative_deviation"
            ].max(),
            "max_robust_score": group[
                "robust_score"
            ].max(),
            "total_excess_estimate": (
                group[BUILDING_ID]
                - group["expected_electricity"]
            ).sum(),
        }

        incidents.append(incident)

    return candidates, incidents


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":

    print("\n========== SUSTAINOPS INCIDENT DETECTOR ==========\n")

    data = load_electricity_data()
    data = add_time_features(data)
    data = calculate_robust_baseline(data)
    data = calculate_anomaly_score(data)

    candidates, threshold = get_candidate_anomalies(data)

    print(f"Building: {BUILDING_ID}")
    print(f"Candidate threshold: {threshold:.4f}")
    print(f"Candidate observations: {len(candidates)}")

    candidates, incidents = form_incidents(candidates)

    print(f"\nMaximum grouping gap: {MAX_GAP_HOURS} hours")
    print(f"Number of incidents: {len(incidents)}")

    print("\n--- Incident Summary ---")

    for incident in incidents:

        print(
            f"\n{incident['incident_id']}"
        )

        print(
            f"Start: {incident['start']}"
        )

        print(
            f"End: {incident['end']}"
        )

        print(
            f"Candidate observations: "
            f"{incident['candidate_count']}"
        )

        print(
            f"Maximum relative deviation: "
            f"{incident['max_relative_deviation']:.2%}"
        )

        print(
            f"Maximum robust score: "
            f"{incident['max_robust_score']:.4f}"
        )

        print(
            f"Estimated excess electricity: "
            f"{incident['total_excess_estimate']:.2f}"
        )

    print("\n===================================================\n")