from pathlib import Path
import sys
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

sys.path.insert(0, str(PROJECT_ROOT / "src"))

from data_loader import load_building_data

BUILDING_ID = "Eagle_education_Wesley"


def prepare_electricity_data(data):
    """
    Load electricity data for the selected building
    and create time features used for historical comparison.
    """

    electricity = data["electricity"][
        ["timestamp", BUILDING_ID]
    ].copy()

    electricity["timestamp"] = pd.to_datetime(
        electricity["timestamp"]
    )

    electricity["month"] = electricity["timestamp"].dt.month
    electricity["day_of_week"] = electricity["timestamp"].dt.dayofweek
    electricity["hour"] = electricity["timestamp"].dt.hour

    return electricity


def find_historical_comparisons(
    electricity,
    incident_start,
    incident_end
):
    """
    Find previous observations with the same
    month, weekday and hour as the incident observations.

    Only observations BEFORE the incident are used.
    """

    incident_mask = (
        (electricity["timestamp"] >= incident_start)
        & (electricity["timestamp"] <= incident_end)
    )

    incident = electricity.loc[incident_mask].copy()

    historical_records = []

    for _, row in incident.iterrows():

        timestamp = row["timestamp"]

        matching_history = electricity[
            (electricity["timestamp"] < timestamp)
            & (electricity["month"] == row["month"])
            & (electricity["day_of_week"] == row["day_of_week"])
            & (electricity["hour"] == row["hour"])
            & (electricity[BUILDING_ID].notna())
        ].copy()

        historical_values = matching_history[
            BUILDING_ID
        ]

        if len(historical_values) == 0:
            expected = np.nan
            history_count = 0

        else:
            expected = historical_values.median()
            history_count = len(historical_values)

        actual = row[BUILDING_ID]

        if pd.isna(actual) or pd.isna(expected):
            deviation = np.nan

        else:
            deviation = (
                (actual - expected)
                / expected
            )

        historical_records.append({
            "timestamp": timestamp,
            "actual_electricity": actual,
            "historical_expected": expected,
            "relative_deviation": deviation,
            "history_count": history_count
        })

    return pd.DataFrame(historical_records)


if __name__ == "__main__":

    print(
        "\n========== SUSTAINOPS HISTORICAL EVIDENCE ==========\n"
    )

    data = load_building_data()

    electricity = prepare_electricity_data(data)

    incident_start = pd.Timestamp(
        "2017-10-04 20:00:00"
    )

    incident_end = pd.Timestamp(
        "2017-10-05 12:00:00"
    )

    evidence = find_historical_comparisons(
        electricity,
        incident_start,
        incident_end
    )

    print(f"Building: {BUILDING_ID}")

    print("\nIncident:")
    print(f"Start: {incident_start}")
    print(f"End:   {incident_end}")

    print("\n--- Historical Evidence ---")

    print(
        evidence.to_string(index=False)
    )

    print(
        "\n======================================================\n"
    )