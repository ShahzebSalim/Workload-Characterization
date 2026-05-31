import argparse
import pandas as pd
from pathlib import Path

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Calculate Inter-Arrival Times (IAT) from hey.csv")
    p.add_argument("--run-id", required=True, help="Name of the run folder in runs/")
    return p.parse_args()

def main():
    args = parse_args()
    
    # Path to the raw hey.csv
    hey_csv = Path("runs") / args.run_id / "hey.csv"
    
    if not hey_csv.exists():
        print(f"Error: Could not find {hey_csv}")
        return

    # Load the data
    print(f"Loading {hey_csv}...")
    df = pd.read_csv(hey_csv)
    
    # Sort by offset just in case hey output it slightly out of order
    df = df.sort_values(by="offset")
    
    # Calculate the difference between consecutive offsets
    # fillna(0) handles the very first request
    df["iat"] = df["offset"].diff().fillna(0)
    
    # Your other scripts (fit_distributions.py) expect a column named "value"
    out_df = pd.DataFrame({"value": df["iat"]})
    
    # Save it to the prometheus folder so fit_distributions.py picks it up automatically!
    out_dir = Path("data/raw") / args.run_id / "prometheus"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    out_path = out_dir / "inter_arrival_times.csv"
    out_df.to_csv(out_path, index=False)
    
    print(f"Success! Calculated {len(out_df)} IAT values.")
    print(f"Saved to: {out_path}")

if __name__ == "__main__":
    main()