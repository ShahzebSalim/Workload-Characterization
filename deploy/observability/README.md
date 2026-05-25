# Observability: Prometheus + Grafana (kube-prometheus-stack)

This is the recommended metrics setup for the assignment.

## Install (Helm)
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

# Install with conservative resource settings for 8GB RAM
helm upgrade --install kps prometheus-community/kube-prometheus-stack \
  -n monitoring \
  -f deploy/observability/values-kind-8gb.yaml
```

## Access Grafana
```bash
kubectl -n monitoring port-forward svc/kps-grafana 3000:80
# open http://localhost:3000
```

Get admin password:
```bash
kubectl -n monitoring get secret kps-grafana -o jsonpath="{.data.admin-password}" | base64 -d; echo
```

## Access Prometheus
```bash
kubectl -n monitoring port-forward svc/kps-kube-prometheus-stack-prometheus 9090:9090
# open http://localhost:9090
```

## What metrics to export for the project
Minimum set (see `scripts/collect/`):
- CPU, memory per pod (`container_cpu_usage_seconds_total`, `container_memory_working_set_bytes`)
- Pod readiness / restarts
- Any HTTP request rate & latency metrics you can scrape (depends on app instrumentation)

If you later add tracing, do it after you have the metrics-based pipeline working.
