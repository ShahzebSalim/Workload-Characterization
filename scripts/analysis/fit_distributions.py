from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as st


@dataclass
class FitResult:
    dist: str
    params: tuple
    ks_stat: float
    ks_pvalue: float
    aic: float


DISTS = {
    "expon": st.expon,
    "pareto": st.pareto,
    "lognorm": st.lognorm,
    "gamma": st.gamma,
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Fit candidate distributions to metric samples")
    p.add_argument("--run-id", required=True)
    p.add_argument(
        "--metric",
        default=None,
        help="CSV basename to fit (e.g., http_latency_p95_seconds.csv). Default: fit all.",
    )
    return p.parse_args()


def fit_one(samples: np.ndarray) -> list[FitResult]:
    results: list[FitResult] = []
    n = len(samples)
    for name, dist in DISTS.items():
        try:
            params = dist.fit(samples)
            # KS test against fitted CDF
            ks = st.kstest(samples, name, args=params)
            # AIC = 2k - 2ln(L)
            ll = np.sum(dist.logpdf(samples, *params))
            k = len(params)
            aic = 2 * k - 2 * ll
            results.append(FitResult(name, params, float(ks.statistic), float(ks.pvalue), float(aic)))
        except Exception:
            continue
    results.sort(key=lambda r: r.aic)
    return results


def ccdf_plot(samples: np.ndarray, out_path: Path, title: str) -> None:
    x = np.sort(samples)
    y = 1.0 - np.arange(1, len(x) + 1) / len(x)
    plt.figure(figsize=(6, 4))
    plt.loglog(x, y, marker=".", linestyle="none")
    plt.xlabel("value")
    plt.ylabel("CCDF")
    plt.title(title)
    plt.grid(True, which="both", ls=":")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close()


def main() -> None:
    args = parse_args()
    in_dir = Path("data/raw") / args.run_id / "prometheus"
    out_dir = Path("data/processed") / args.run_id
    fig_dir = out_dir / "figures"

    csvs = [in_dir / args.metric] if args.metric else sorted(in_dir.glob("*.csv"))

    rows = []
    for csv in csvs:
        if not csv.exists():
            continue
        df = pd.read_csv(csv)
        if "value" not in df.columns or df.empty:
            continue

        s = df["value"].dropna().astype(float)
        # For distribution fitting, we focus on positive-valued metrics
        s = s[s > 0]
        if len(s) < 50:
            continue

        samples = s.to_numpy()
        fits = fit_one(samples)
        if not fits:
            continue

        best = fits[0]
        for r in fits:
            rows.append(
                {
                    "metric": csv.name,
                    "dist": r.dist,
                    "ks_stat": r.ks_stat,
                    "ks_pvalue": r.ks_pvalue,
                    "aic": r.aic,
                    "params": str(tuple(round(float(x), 6) for x in r.params)),
                    "best": r.dist == best.dist,
                }
            )

        ccdf_plot(samples, fig_dir / f"ccdf_{csv.stem}.png", f"CCDF: {csv.stem}")

    if not rows:
        raise SystemExit("No metrics had enough positive samples to fit. Export more data or adjust queries.")

    out_df = pd.DataFrame(rows).sort_values(["metric", "aic"], ascending=[True, True])
    out_path = out_dir / "distribution_fits.csv"
    out_df.to_csv(out_path, index=False)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
