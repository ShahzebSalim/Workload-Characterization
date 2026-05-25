# Workload Characterization (Software Performance Engineering)

Microservice workload trace collection and statistical characterization (arrival + service processes) for a Kubernetes-deployed benchmark.

## Project objective
Collect and analyze workload traces from a Kubernetes-deployed microservice benchmark to characterize:
- **Arrivals** (arrival rate process, burstiness, autocorrelation, stationarity)
- **Service times** (per-service request latency / service-time proxies)
- **Resource behavior** (CPU/memory, queue lengths where available)

You will:
1) deploy a benchmark microservice app on Kubernetes
2) run a controlled load generator
3) collect traces + metrics
4) fit distributions and analyze temporal structure
5) produce a short report with findings and modeling implications

## Recommended testbed (default)
**Google Online Boutique (microservices-demo)** because it includes a built-in load generator and is widely used in research/teaching.

You can switch to Sock Shop or µBench later—this repo is structured to keep data + scripts portable.

## Repo layout
- `deploy/` Kubernetes manifests / Helm notes
- `scripts/` data collection + analysis pipeline
- `notebooks/` exploratory analysis
- `data/` local datasets (not committed by default)
- `report/` report template

## Quick start (local cluster)
### 1) Create a Kubernetes cluster
Pick one:
- **kind** (recommended): https://kind.sigs.k8s.io/
- **minikube**

### 2) Deploy Online Boutique
See `deploy/online-boutique/README.md`.

### 3) Install Prometheus + Grafana
See `deploy/observability/README.md`.

### 4) Generate load + collect data
See `scripts/collect/README.md`.

### 5) Run analysis
See `scripts/analysis/README.md`.

## Deliverables checklist
- [ ] Dataset (metrics exports + trace extracts) and scripts used to collect them
- [ ] Analysis scripts fitting distributions (Poisson/exponential/Pareto/heavy-tailed)
- [ ] Autocorrelation / burstiness / stationarity analysis
- [ ] Report with descriptive stats, fitted models, interpretation

## Notes
- This repo intentionally separates **collection** from **analysis** so you can re-run analysis on multiple data captures.
- Start with Prometheus metrics; optionally add tracing (OpenTelemetry/Jaeger) for richer per-request service-time breakdowns.
