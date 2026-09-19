from pathlib import Path
import sys
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

sys.path.insert(0, str(PROJECT_ROOT / "src"))

from data_loader import load_building_data

BUILDING_ID = "Eagle_education_Wesley"


def prepare_meter_data(data, building_id):
    """
    Extract the selected building's meter readings
    and convert timestamps into a common datetime format.
    """

    result = {}

    meter_files = {
        "electricity": "electricity",
        "steam": "steam",
        "chilled_water": "chilled_water",
        "hot_water": "hot_water",
    }

    for meter_name, key in meter_files.items():

        meter_data = data[key][
            ["timestamp", building_id]
        ].copy()

        meter_data["timestamp"] = pd.to_datetime(
            meter_data["timestamp"]
        )

        meter_data = meter_data.rename(
            columns={
                building_id: meter_name
            }
        )

        result[meter_name] = meter_data

    return result


def get_incident_evidence(
    meter_data,
    start_time,
    end_time
):
    """
    Extract supporting meter evidence for an incident.
    """

    evidence = {}

    for meter_name, data in meter_data.items():

        mask = (
            (data["timestamp"] >= start_time)
            & (data["timestamp"] <= end_time)
        )

        incident_data = data.loc[mask].copy()

        evidence[meter_name] = incident_data

    return evidence


def summarize_meter_evidence(evidence):

    summary = []

    for meter_name, data in evidence.items():

        values = data[meter_name].dropna()

        if len(values) == 0:
            summary.append({
                "meter": meter_name,
                "observations": 0,
                "mean": None,
                "minimum": None,
                "maximum": None,
            })

        else:
            summary.append({
                "meter": meter_name,
                "observations": len(values),
                "mean": values.mean(),
                "minimum": values.min(),
                "maximum": values.max(),
            })

    return pd.DataFrame(summary)


if __name__ == "__main__":

    print(
        "\n========== SUSTAINOPS INVESTIGATION ==========\n"
    )

    data = load_building_data()

    meter_data = prepare_meter_data(
        data,
        BUILDING_ID
    )

    start_time = pd.Timestamp(
        "2017-10-04 20:00:00"
    )

    end_time = pd.Timestamp(
        "2017-10-05 12:00:00"
    )

    evidence = get_incident_evidence(
        meter_data,
        start_time,
        end_time
    )

    summary = summarize_meter_evidence(
        evidence
    )

    print(f"Building: {BUILDING_ID}")

    print("\nIncident:")
    print(f"Start: {start_time}")
    print(f"End:   {end_time}")

    print("\n--- Supporting Meter Evidence ---")
    print(summary.to_string(index=False))

    print(
        "\n================================================\n"
    )