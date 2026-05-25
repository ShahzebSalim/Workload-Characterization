from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller, kpss


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Time-series diagnostics: ACF + stationarity tests")
    p.add_argument("--run-id", required=True)
    p.add_argument("--max-lag", type=int, default=60)
    return p.parse_args()


def acf(x: np.ndarray, max_lag: int) -> np.ndarray:
    x = x.astype(float)
    x = x - np.mean(x)
    denom = np.dot(x, x)
    out = np.empty(max_lag + 1)
    out[0] = 1.0
    for k in range(1, max_lag + 1):
        out[k] = np.dot(x[:-k], x[k:]) / denom if denom != 0 else 0.0
    return out


def plot_acf(values: np.ndarray, max_lag: int, out_path: Path, title: str) -> None:
    a = acf(values, max_lag)
    plt.figure(figsize=(7, 3.5))
    plt.stem(range(len(a)), a, use_line_collection=True)
    plt.xlabel("lag")
    plt.ylabel("ACF")
    plt.title(title)
    plt.grid(True, ls=":")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close()


def stationarity_tests(x: np.ndarray) -> dict:
    out = {}
    # ADF: H0 = unit root (non-stationary)
    adf = adfuller(x, autolag="AIC")
    out["adf_stat"] = float(adf[0])
    out["adf_pvalue"] = float(adf[1])

    # KPSS: H0 = stationary
    try:
        k = kpss(x, regression="c", nlags="auto")
        out["kpss_stat"] = float(k[0])
        out["kpss_pvalue"] = float(k[1])
    except Exception:
        out["kpss_stat"] = float("nan")
        out["kpss_pvalue"] = float("nan")
    return out


def main() -> None:
    args = parse_args()
    in_dir = Path("data/raw") / args.run_id / "prometheus"
    out_dir = Path("data/processed") / args.run_id
    fig_dir = out_dir / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for csv in sorted(in_dir.glob("*.csv")):
        df = pd.read_csv(csv)
        if df.empty or "value" not in df.columns:
            continue

        s = df["value"].dropna().astype(float)
        if len(s) < max(50, args.max_lag + 5):
            continue

        x = s.to_numpy()
        plot_acf(x, args.max_lag, fig_dir / f"acf_{csv.stem}.png", f"ACF: {csv.stem}")
        tests = stationarity_tests(x)

        rows.append(
            {
                "metric": csv.name,
                "n": int(len(x)),
                **tests,
            }
        )

    if not rows:
        raise SystemExit("No suitable time series found for diagnostics.")

    out_df = pd.DataFrame(rows).sort_values("metric")
    out_path = out_dir / "time_series_diagnostics.csv"
    out_df.to_csv(out_path, index=False)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
