# Analysis (Python + uv)

This project uses **uv** to manage a lightweight Python environment on macOS.

## Setup
Install uv:
```bash
brew install uv
```

Create venv + install deps:
```bash
uv venv
uv pip install -r scripts/analysis/requirements.txt
```

## Run analysis pipeline
After you export CSV files under `data/raw/<run_id>/prometheus/`:

### 1) Compute descriptive stats
```bash
python scripts/analysis/descriptive_stats.py --run-id <run_id>
```

### 2) Fit distributions
```bash
python scripts/analysis/fit_distributions.py --run-id <run_id>
```

### 3) Autocorrelation + stationarity
```bash
python scripts/analysis/time_series_diagnostics.py --run-id <run_id>
```

Outputs go to:
- `data/processed/<run_id>/...`
- `data/processed/<run_id>/figures/...`

## Notes on meeting requirements
- **Arrival rates**: analyze request-rate time series (if you have HTTP metrics). If not, start with frontend CPU as a proxy and add HTTP metrics later.
- **Service times**: analyze latency histograms/quantiles if available.
- **Burstiness/autocorrelation/stationarity**: the diagnostics script computes ACF and ADF/KPSS tests for each chosen metric.
