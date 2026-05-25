# Collect scripts

This folder contains scripts to export Prometheus time-series to CSV for workload characterization.

## Prerequisites
- Prometheus reachable at `http://localhost:9090` (port-forward in `deploy/observability/README.md`)
- Python environment created via `uv` (see `scripts/analysis/README.md`)

## Typical workflow
1) Start port-forward to Prometheus.
2) Run load for a fixed duration (e.g., 20 minutes).
3) Export metrics for the same time window.
4) Run analysis.

## Define a run window
Pick a run id and explicit timestamps (UTC ISO8601 recommended):
- `RUN_ID=2026-05-25-kind-ob-20m`
- `START=2026-05-25T20:00:00Z`
- `END=2026-05-25T20:20:00Z`

## Export Kubernetes resource metrics (always available)
```bash
python scripts/collect/export_prometheus_range.py \
  --run-id "$RUN_ID" \
  --start "$START" --end "$END" \
  --step 15 \
  --query-file scripts/collect/queries/k8s_resources.yaml
```

## Export HTTP request/latency metrics (if present)
If your app exposes HTTP metrics (Prometheus format), add them to scrape targets and then export:
```bash
python scripts/collect/export_prometheus_range.py \
  --run-id "$RUN_ID" \
  --start "$START" --end "$END" \
  --step 5 \
  --query-file scripts/collect/queries/http_workload.yaml
```

Outputs go to:
- `data/raw/<run_id>/prometheus/<metric_name>.csv`

## Notes
- If you don’t have per-service HTTP metrics yet, you can still complete most of the project using:
  - CPU/mem utilization as load/saturation indicators
  - frontend pod-level metrics
  - optional: add a simple NGINX ingress with metrics later
