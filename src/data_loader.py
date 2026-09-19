from pathlib import Path
import pandas as pd


# -----------------------------
# Project paths
# -----------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


# -----------------------------
# Target building
# -----------------------------

BUILDING_ID = "Eagle_education_Wesley"


# -----------------------------
# Load metadata
# -----------------------------

def load_metadata():
    """Load building metadata."""
    
    path = DATA_DIR / "metadata.csv"
    
    metadata = pd.read_csv(path)
    
    return metadata


# -----------------------------
# Load a meter dataset
# -----------------------------

def load_meter_data(filename):
    """Load a meter CSV file."""
    
    path = DATA_DIR / filename
    
    data = pd.read_csv(path)
    
    return data


# -----------------------------
# Load Wesley's data
# -----------------------------

def load_building_data():
    """Load all available meter data for the selected building."""
    
    metadata = load_metadata()
    
    electricity = load_meter_data("electricity_cleaned.csv")
    steam = load_meter_data("steam_cleaned.csv")
    chilled_water = load_meter_data("chilledwater_cleaned.csv")
    hot_water = load_meter_data("hotwater_cleaned.csv")
    
    return {
        "metadata": metadata,
        "electricity": electricity,
        "steam": steam,
        "chilled_water": chilled_water,
        "hot_water": hot_water,
    }


# -----------------------------
# Test the loader
# -----------------------------

if __name__ == "__main__":
    
    data = load_building_data()
    
    print("\n========== SUSTAINOPS DATA LOADER ==========\n")
    
    print("Target building:")
    print(BUILDING_ID)
    
    print("\nMetadata shape:")
    print(data["metadata"].shape)
    
    print("\nElectricity shape:")
    print(data["electricity"].shape)
    
    print("\nSteam shape:")
    print(data["steam"].shape)
    
    print("\nChilled water shape:")
    print(data["chilled_water"].shape)
    
    print("\nHot water shape:")
    print(data["hot_water"].shape)
    
    print("\n=============================================\n")