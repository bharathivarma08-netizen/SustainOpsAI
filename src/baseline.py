from pathlib import Path
import numpy as np
import pandas as pd


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

BUILDING_ID = "Eagle_education_Wesley"


# --------------------------------------------------
# LOAD ELECTRICITY DATA
# --------------------------------------------------

def load_electricity_data():

    path = DATA_DIR / "electricity_cleaned.csv"

    data = pd.read_csv(
        path,
        usecols=["timestamp", BUILDING_ID]
    )

    data["timestamp"] = pd.to_datetime(data["timestamp"])

    data = data.sort_values("timestamp").reset_index(drop=True)

    return data


# --------------------------------------------------
# ADD TIME FEATURES
# --------------------------------------------------

def add_time_features(data):

    data = data.copy()

    data["month"] = data["timestamp"].dt.month
    data["day_of_week"] = data["timestamp"].dt.dayofweek
    data["hour"] = data["timestamp"].dt.hour

    return data


# --------------------------------------------------
# BUILD TIME-AWARE HISTORICAL BASELINE
# --------------------------------------------------

def calculate_historical_baseline(data):

    data = data.copy()

    # Column where we will store the expected value
    data["expected_electricity"] = np.nan

    # Store previous observations for each
    # month + day-of-week + hour combination
    history = {}

    for index, row in data.iterrows():

        value = row[BUILDING_ID]

        key = (
            row["month"],
            row["day_of_week"],
            row["hour"]
        )

        # Calculate expected value only from
        # observations that occurred before this timestamp
        if key in history and len(history[key]) > 0:

            data.loc[index, "expected_electricity"] = (
                np.median(history[key])
            )

        # Add current observation to history
        # only after calculating its baseline
        if pd.notna(value):

            if key not in history:
                history[key] = []

            history[key].append(value)

    return data


# --------------------------------------------------
# CALCULATE DEVIATION
# --------------------------------------------------

def calculate_deviation(data):

    data = data.copy()

    data["absolute_deviation"] = (
        data[BUILDING_ID]
        - data["expected_electricity"]
    )

    data["relative_deviation"] = (
        data["absolute_deviation"]
        / data["expected_electricity"]
    )

    return data


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    print("\n========== SUSTAINOPS HISTORICAL BASELINE ==========\n")

    data = load_electricity_data()

    data = add_time_features(data)

    data = calculate_historical_baseline(data)

    data = calculate_deviation(data)

    print(f"Building: {BUILDING_ID}")

    print("\n--- Sample baseline records ---")

    print(
        data[
            [
                "timestamp",
                BUILDING_ID,
                "month",
                "day_of_week",
                "hour",
                "expected_electricity",
                "absolute_deviation",
                "relative_deviation"
            ]
        ].head(30).to_string(index=False)
    )

    valid_baselines = data["expected_electricity"].notna().sum()

    print("\n--- Baseline Coverage ---")
    print(f"Total observations: {len(data)}")
    print(f"Observations with baseline: {valid_baselines}")
    print(
        f"Observations without baseline: "
        f"{len(data) - valid_baselines}"
    )

    print("\n=====================================================\n")