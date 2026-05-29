import json, csv, sys

# usage: python3 prom_to_csv.py input.json output.csv
inp, outp = sys.argv[1], sys.argv[2]

with open(inp, "r") as f:
    payload = json.load(f)

result = payload["data"]["result"]
if not result:
    raise SystemExit(f"No series in {inp} (empty result).")

# Collect all timestamps across all series
all_ts = sorted({ts for series in result for ts, _ in series["values"]})

# Build per-series map: name -> {ts: value}
series_names = []
series_map = {}

def series_name(metric: dict) -> str:
    # Prefer pod; fall back to __name__ and then a generic label
    return metric.get("pod") or metric.get("__name__") or "series"

for series in result:
    metric = series.get("metric", {})
    name = series_name(metric)

    # Ensure unique column name
    base = name
    i = 2
    while name in series_map:
        name = f"{base}_{i}"
        i += 1

    series_names.append(name)
    series_map[name] = {ts: val for ts, val in series["values"]}

with open(outp, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["timestamp"] + series_names)
    for ts in all_ts:
        w.writerow([ts] + [series_map[n].get(ts, "") for n in series_names])

print(f"Wrote {outp}: {len(all_ts)} rows, {len(series_names)} series")
