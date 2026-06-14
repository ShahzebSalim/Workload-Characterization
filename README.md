# Workload Characterization: Google Online Boutique

**Authors:** Shahzeb Salim & Aneeza Maroof
**Course:** Software Performance Engineering

**Please see the `Shahzeb_Aneeza_Workload_Report.pdf` file for the comprehensive narrative on our methodology, smoke testing, failure analysis, and figure sourcing.**

## Project Overview
This repository contains the infrastructure scripts, load generation configurations, and statistical analysis code required to characterize the workload of the Google Online Boutique microservice application deployed on a local Kubernetes cluster.

## Project Flow & Reproducibility

### Phase 1: Infrastructure & Observability
The System Under Test (SUT) was deployed using `kind` (Kubernetes IN Docker) on a local Apple M1 environment.
* **Application:** Deployed the standard 11-tier Google Online Boutique microservice architecture.
* **Observability:** Deployed the `kube-prometheus-stack` to establish Prometheus for metric scraping (CPU, Memory, Network) and Grafana for live visualization. (See the `deploy/` folder for manifest configurations).

### Phase 2: Load Generation & Metric Collection
Load generation was orchestrated using the `hey` utility. 
To reproduce the data collection:
1. Ensure the `boutique` namespace is running.
2. Execute the shell script: `./scripts/run_experiment.sh`
This script applies the designated concurrency load and automatically extracts the telemetry metrics from Prometheus.

### Phase 3: Statistical Analysis
The raw data is processed using Python (Pandas, SciPy, Statsmodels).
To reproduce the mathematical fitting and charts:
1. Navigate to the analysis directory: `cd scripts/analysis`
2. Run the distribution fitter: `python3 fit_distributions.py`
3. Run the time-series diagnostics: `python3 time_series_diagnostics.py`

*Note: Due to memory saturation boundaries (OOMKilled events) on the local host during high-load tests, the final distribution fitting was isolated to the `pure_math_run` dataset to ensure uncorrupted mathematical modeling.*

## Data Architecture
* `runs/`: Contains the raw Prometheus JSON exports and `hey` CSV traces generated directly by our load-testing script. This serves as the raw telemetry proof of our test executions.
* `data/processed/`: Contains our cleaned, filtered datasets (e.g., isolating HTTP 200 OK responses) used for the final mathematical distribution fitting and time-series analysis.