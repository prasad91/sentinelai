import json
import os
from pathlib import Path

def generate_report(results, out_file="output/report.json", append=True):
    Path("output").mkdir(exist_ok=True)
    
    if append and os.path.exists(out_file):
        with open(out_file, "r") as f:
            try:
                existing = json.load(f)
            except Exception as e:
                print(f"❌ Error parsing existing report: {e}")
                existing = []
        combined = existing + results
    else:
        combined = results

    with open(out_file, "w") as f:
        json.dump(combined, f, indent=2)

def delete_old_report(out_file="output/report.json"):
    Path("output").mkdir(exist_ok=True)

    if os.path.exists(out_file):
        os.remove(out_file)
        print("🗑️ Removed old report...")