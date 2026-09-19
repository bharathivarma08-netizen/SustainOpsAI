from pathlib import Path
import numpy as np
import pandas as pd


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

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
# CALCULATE HISTORICAL ROBUST STATISTICS
# --------------------------------------------------

def calculate_robust_baseline(data):
    data = data.copy()

    data["expected_electricity"] = np.nan
    data["mad"] = np.nan
    data["history_count"] = 0

    history = {}

    MIN_HISTORY = 4

    for index, row in data.iterrows():

        value = row[BUILDING_ID]

        key = (
            row["month"],
            row["day_of_week"],
            row["hour"]
        )

        historical_values = history.get(key, [])

        data.loc[index, "history_count"] = len(historical_values)

        if len(historical_values) >= MIN_HISTORY:

            historical_values = np.array(historical_values)

            median_value = np.median(historical_values)

            mad_value = np.median(
                np.abs(historical_values - median_value)
            )

            data.loc[index, "expected_electricity"] = median_value
            data.loc[index, "mad"] = mad_value

        if pd.notna(value):

            if key not in history:
                history[key] = []

            history[key].append(value)

    return data


# --------------------------------------------------
# CALCULATE ROBUST ANOMALY SCORE
# --------------------------------------------------

def calculate_anomaly_score(data):
    data = data.copy()

    data["absolute_deviation"] = (
        data[BUILDING_ID] - data["expected_electricity"]
    )

    data["relative_deviation"] = (
        data["absolute_deviation"]
        / data["expected_electricity"]
    )

    data["robust_score"] = np.nan

    # Use MAD-based score when MAD is positive
    valid_mad = data["mad"] > 0

    data.loc[valid_mad, "robust_score"] = (
        0.6745
        * data.loc[valid_mad, "absolute_deviation"]
        / data.loc[valid_mad, "mad"]
    )

    # Classify direction
    data["direction"] = "INSUFFICIENT_EVIDENCE"

    sufficient_history = data["history_count"] >= 4

    data.loc[
        sufficient_history & (data["absolute_deviation"] > 0),
        "direction"
    ] = "HIGH"

    data.loc[
        sufficient_history & (data["absolute_deviation"] < 0),
        "direction"
    ] = "LOW"

    data.loc[
        sufficient_history & (data["absolute_deviation"] == 0),
        "direction"
    ] = "NORMAL"

    return data


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    print("\n========== SUSTAINOPS ANOMALY DETECTOR ==========\n")

    data = load_electricity_data()

    data = add_time_features(data)

    data = calculate_robust_baseline(data)

    data = calculate_anomaly_score(data)

    print(f"Building: {BUILDING_ID}")

    print("\n--- Candidate Event Analysis ---")

    candidate_times = pd.to_datetime([
        "2016-03-23 16:00:00",
        "2017-04-12 16:00:00"
    ])

    candidates = data[
        data["timestamp"].isin(candidate_times)
    ]

    print(
        candidates[
            [
                "timestamp",
                BUILDING_ID,
                "expected_electricity",
                "mad",
                "absolute_deviation",
                "relative_deviation",
                "robust_score"
            ]
        ].to_string(index=False)
    )

    print("\n--- Score Summary ---")

    scores = data["robust_score"].dropna()

    print(f"Valid anomaly scores: {len(scores)}")
    print(f"Median score: {scores.median():.2f}")
    print(f"Maximum score: {scores.max():.2f}")
    print(
        f"95th percentile: "
        f"{scores.quantile(0.95):.2f}"
    )
    print(
        f"99th percentile: "
        f"{scores.quantile(0.99):.2f}"
    )

    print("\n=================================================\n")