# Report template (Workload Characterization)

Use this outline to write your report.

## 1. System under test (SUT)
- Cluster setup (kind on Docker Desktop; MacBook Air M1 8GB)
- Benchmark app (Online Boutique)
- Version/commit (record the exact manifest source)

## 2. Measurement & data collection
- Monitoring stack (kube-prometheus-stack)
- Metrics exported (list PromQL queries)
- Load generation method and duration
- Time window (start/end UTC timestamps)

## 3. Workload characterization
### 3.1 Arrival process
- Arrival rate time series
- Burstiness (e.g., index of dispersion, peak-to-mean)
- Autocorrelation (ACF plots)
- Stationarity (ADF/KPSS)

### 3.2 Service process (service-time proxies)
- Latency distributions (p50/p95/p99; histograms if available)
- Candidate distribution fits (exponential/gamma/lognormal/Pareto)
- Goodness-of-fit (KS + AIC comparison)

### 3.3 Resource behavior
- CPU and memory per pod
- Identify saturation periods / hotspots

## 4. Interpretation
- Which classical assumptions hold? (Poisson arrivals? exponential service times? independence?)
- Implications for queueing model accuracy

## 5. Reproducibility
- Commands to deploy
- Commands to collect data
- Commands to run analysis

## Appendix
- Figures (CCDF, ACF)
- Tables of fitted parameters
