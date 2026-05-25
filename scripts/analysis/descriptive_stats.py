from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compute descriptive stats for exported Prometheus CSVs")
    p.add_argument("--run-id", required=True)
    return p.parse_args()


def summarize_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    if df.empty or "value" not in df.columns:
        return pd.DataFrame()

    s = df["value"].dropna()
    out = {
        "file": path.name,
        "n": int(s.shape[0]),
        "mean": float(s.mean()),
        "std": float(s.std(ddof=1)) if s.shape[0] > 1 else 0.0,
        "min": float(s.min()),
        "p50": float(s.quantile(0.50)),
        "p90": float(s.quantile(0.90)),
        "p95": float(s.quantile(0.95)),
        "p99": float(s.quantile(0.99)),
        "max": float(s.max()),
    }
    return pd.DataFrame([out])


def main() -> None:
    args = parse_args()
    in_dir = Path("data/raw") / args.run_id / "prometheus"
    out_dir = Path("data/processed") / args.run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for csv in sorted(in_dir.glob("*.csv")):
        summ = summarize_csv(csv)
        if not summ.empty:
            rows.append(summ)

    if not rows:
        raise SystemExit(f"No usable CSVs found under {in_dir} (need a 'value' column)")

    report = pd.concat(rows, ignore_index=True)
    out_path = out_dir / "descriptive_stats.csv"
    report.to_csv(out_path, index=False)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
