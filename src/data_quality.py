from pathlib import Path
import pandas as pd


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

BUILDING_ID = "Eagle_education_Wesley"


# --------------------------------------------------
# LOAD ONLY THE REQUIRED BUILDING DATA
# --------------------------------------------------

def load_electricity_data():
    """
    Load timestamp and electricity data
    for the selected building only.
    """

    path = DATA_DIR / "electricity_cleaned.csv"

    data = pd.read_csv(
        path,
        usecols=["timestamp", BUILDING_ID]
    )

    data["timestamp"] = pd.to_datetime(data["timestamp"])

    data = data.sort_values("timestamp").reset_index(drop=True)

    return data


# --------------------------------------------------
# DATA QUALITY ANALYSIS
# --------------------------------------------------

def analyze_data_quality(data):

    timestamp = data["timestamp"]
    electricity = data[BUILDING_ID]

    report = {}

    # Number of observations
    report["total_observations"] = len(data)

    # Timestamp checks
    report["missing_timestamps"] = timestamp.isna().sum()
    report["duplicate_timestamps"] = timestamp.duplicated().sum()

    # Electricity checks
    report["missing_values"] = electricity.isna().sum()
    report["zero_values"] = (electricity == 0).sum()
    report["negative_values"] = (electricity < 0).sum()

    # Statistical summary
    report["minimum"] = electricity.min()
    report["maximum"] = electricity.max()
    report["mean"] = electricity.mean()
    report["median"] = electricity.median()
    report["standard_deviation"] = electricity.std()

    return report


# --------------------------------------------------
# FIND CONSECUTIVE MISSING PERIODS
# --------------------------------------------------

def find_missing_runs(data):

    missing = data[BUILDING_ID].isna()

    groups = missing.ne(missing.shift()).cumsum()

    missing_runs = []

    for _, group in data[missing].groupby(groups[missing]):

        start_time = group["timestamp"].iloc[0]
        end_time = group["timestamp"].iloc[-1]

        duration_hours = len(group)

        missing_runs.append({
            "start": start_time,
            "end": end_time,
            "hours": duration_hours
        })

    return missing_runs


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    print("\n========== SUSTAINOPS DATA QUALITY ==========\n")

    data = load_electricity_data()

    report = analyze_data_quality(data)

    print(f"Building: {BUILDING_ID}")
    print(f"Observations: {report['total_observations']}")

    print("\n--- Timestamp Quality ---")
    print(f"Missing timestamps: {report['missing_timestamps']}")
    print(f"Duplicate timestamps: {report['duplicate_timestamps']}")

    print("\n--- Electricity Quality ---")
    print(f"Missing values: {report['missing_values']}")
    print(f"Zero values: {report['zero_values']}")
    print(f"Negative values: {report['negative_values']}")

    print("\n--- Electricity Statistics ---")
    print(f"Minimum: {report['minimum']:.2f}")
    print(f"Maximum: {report['maximum']:.2f}")
    print(f"Mean: {report['mean']:.2f}")
    print(f"Median: {report['median']:.2f}")
    print(f"Standard deviation: {report['standard_deviation']:.2f}")

    missing_runs = find_missing_runs(data)

    print("\n--- Missing Value Runs ---")
    print(f"Number of missing runs: {len(missing_runs)}")

    if missing_runs:
        longest_run = max(missing_runs, key=lambda x: x["hours"])

        print(
            f"Longest missing run: "
            f"{longest_run['hours']} hours"
        )

        print(
            f"From: {longest_run['start']}"
        )

        print(
            f"To: {longest_run['end']}"
        )

    print("\n=============================================\n")