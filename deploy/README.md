# Deployment guide (kind + Online Boutique + Observability)

This project is designed for a **MacBook Air M1 (8GB)** using **Docker Desktop** + **kind**.

## Prerequisites
- Docker Desktop for Mac
- kubectl
- kind

## Step 1 — Create a kind cluster
Recommended (single node to save RAM):

```bash
kind create cluster --name spe-wc
kubectl cluster-info --context kind-spe-wc
```

If you run out of RAM later, keep it single-node and reduce Prometheus retention (see below).

## Step 2 — Deploy Online Boutique
Follow: `deploy/online-boutique/README.md`

## Step 3 — Deploy Prometheus + Grafana
Follow: `deploy/observability/README.md`

## Step 4 — Generate load + collect datasets
Follow: `scripts/collect/README.md`

## Step 5 — Run analysis
Follow: `scripts/analysis/README.md`
