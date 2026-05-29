#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./run_experiment.sh <run_name> <duration> <concurrency> <q_per_worker> <url>
# Example:
#   ./run_experiment.sh run1 10m 10 20 http://127.0.0.1:8080/

RUN_NAME="${1:-run1}"
DURATION="${2:-10m}"
CONCURRENCY="${3:-10}"
Q="${4:-20}"
URL="${5:-http://127.0.0.1:8080/}"

PROM="http://localhost:9090"
NAMESPACE="boutique"

mkdir -p runs/"$RUN_NAME"

echo "Starting run: $RUN_NAME"
START=$(date +%s)

# Run load test and store per-request results
hey -z "$DURATION" -c "$CONCURRENCY" -q "$Q" -o csv "$URL" > runs/"$RUN_NAME"/hey.csv

END=$(date +%s)
echo "Run finished. start=$START end=$END"

# Add buffer so rate([5m]) has enough context near the edges
BUF=300  # 5 minutes
EXPORT_START=$((START-BUF))
EXPORT_END=$((END+BUF))
STEP=5

# CPU per pod
curl -s -G "$PROM/api/v1/query_range" \
  --data-urlencode "query=sum by (pod) (rate(container_cpu_usage_seconds_total{namespace=\"$NAMESPACE\"}[5m]))" \
  --data-urlencode "start=$EXPORT_START" \
  --data-urlencode "end=$EXPORT_END" \
  --data-urlencode "step=$STEP" \
  -o runs/"$RUN_NAME"/cpu_by_pod.json

# Mem per pod
curl -s -G "$PROM/api/v1/query_range" \
  --data-urlencode "query=sum by (pod) (container_memory_working_set_bytes{namespace=\"$NAMESPACE\"})" \
  --data-urlencode "start=$EXPORT_START" \
  --data-urlencode "end=$EXPORT_END" \
  --data-urlencode "step=$STEP" \
  -o runs/"$RUN_NAME"/mem_by_pod.json

# Optional: total CPU + total mem
curl -s -G "$PROM/api/v1/query_range" \
  --data-urlencode "query=sum(rate(container_cpu_usage_seconds_total{namespace=\"$NAMESPACE\"}[5m]))" \
  --data-urlencode "start=$EXPORT_START" \
  --data-urlencode "end=$EXPORT_END" \
  --data-urlencode "step=$STEP" \
  -o runs/"$RUN_NAME"/cpu_total.json

curl -s -G "$PROM/api/v1/query_range" \
  --data-urlencode "query=sum(container_memory_working_set_bytes{namespace=\"$NAMESPACE\"})" \
  --data-urlencode "start=$EXPORT_START" \
  --data-urlencode "end=$EXPORT_END" \
  --data-urlencode "step=$STEP" \
  -o runs/"$RUN_NAME"/mem_total.json

# Save metadata for reproducibility
cat > runs/"$RUN_NAME"/meta.txt <<EOF
run_name=$RUN_NAME
start_epoch=$START
end_epoch=$END
export_start_epoch=$EXPORT_START
export_end_epoch=$EXPORT_END
step=$STEP
duration=$DURATION
concurrency=$CONCURRENCY
q_per_worker=$Q
url=$URL
EOF

echo "Saved: runs/$RUN_NAME/{hey.csv,cpu_by_pod.json,mem_by_pod.json,...}"
