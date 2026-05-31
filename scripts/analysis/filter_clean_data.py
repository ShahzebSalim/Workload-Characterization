import pandas as pd
import argparse
from pathlib import Path

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--run-id", required=True)
    args = p.parse_args()

    input_path = Path("runs") / args.run_id / "hey.csv"
    output_path = Path("runs") / args.run_id / "clean_hey.csv"
    
    df = pd.read_csv(input_path)
    
    # Filter: Keep only successful 200 OK responses
    clean_df = df[df["status-code"] == 200].copy()
    
    # Save the clean version
    clean_df.to_csv(output_path, index=False)
    print(f"Cleaned! Kept {len(clean_df)} successful requests out of {len(df)} total.")
    print(f"File saved to: {output_path}")

if __name__ == "__main__":
    main()
    