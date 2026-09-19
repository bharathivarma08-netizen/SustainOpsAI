import json
from pathlib import Path

path = Path("outputs/INC-016_investigation.json")

with path.open("r", encoding="utf-8") as f:
    data = json.load(f)


def find_scoring(obj, path="root"):
    if isinstance(obj, dict):
        for key, value in obj.items():
            current_path = f"{path}.{key}"

            if "scor" in key.lower() or "hypoth" in key.lower():
                print(f"\n--- {current_path} ---")
                print(json.dumps(value, indent=2, ensure_ascii=False))

            find_scoring(value, current_path)

    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            find_scoring(value, f"{path}[{i}]")


find_scoring(data)