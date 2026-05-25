# Online Boutique deployment

We use **Google Online Boutique (microservices-demo)** as the benchmark testbed.

## Deploy
```bash
# Create namespace
kubectl create namespace boutique --dry-run=client -o yaml | kubectl apply -f -

# Apply upstream manifests (recommended approach)
# NOTE: This repo does not vendor upstream YAML to keep it lightweight.
# If you need fully offline reproducibility, vendor the release manifests into deploy/online-boutique/upstream/.

kubectl apply -n boutique -f https://raw.githubusercontent.com/GoogleCloudPlatform/microservices-demo/main/release/kubernetes-manifests.yaml
```

## Verify
```bash
kubectl -n boutique get pods
```

## Access frontend
Option A (port-forward):
```bash
kubectl -n boutique port-forward svc/frontend 8080:80
# open http://localhost:8080
```

Option B (Ingress) is optional and not recommended for the 8GB setup.

## Load generator
Online Boutique includes a load generator deployment. You can scale it to control load:
```bash
kubectl -n boutique get deploy loadgenerator
kubectl -n boutique scale deploy/loadgenerator --replicas=1
```

To increase load, increase replicas (watch resource use):
```bash
kubectl -n boutique scale deploy/loadgenerator --replicas=2
```

## Notes for workload characterization
- For **arrival rate**, use request-rate metrics from your ingress / frontend / service mesh if present.
  If you deploy only the upstream manifests, you may rely on frontend HTTP metrics if exposed, otherwise use Kubernetes-level proxies (see collect scripts).
- For **service-time**, prefer HTTP latency histograms if available.

If metrics are missing in your deployment, we’ll attach monitoring via `kube-prometheus-stack` and use K8s + cAdvisor metrics (CPU/mem) plus application-level where available.
