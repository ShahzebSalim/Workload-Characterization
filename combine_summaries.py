import json, glob, csv, os

summaries = sorted(glob.glob("runs/*/summary.json"))
if not summaries:
    raise SystemExit("No runs/*/summary.json files found. Run summarize_run.py first.")

rows = []
for path in summaries:
    with open(path) as f:
        s = json.load(f)

    run_name = s["run"]["name"]
    hey = s["hey"]
    lat = hey["latency_seconds"]
    prom = s["prometheus"]

    rows.append({
        "run": run_name,
        "rps": hey["arrival_rate_rps"],
        "requests": hey["requests"],
        "mean_s": lat["mean"],
        "p95_s": lat["p95"],
        "p99_s": lat["p99"],
        "error_fraction": hey["error_fraction"],
        "cpu_total_mean_cores": prom["cpu_total_mean_cores"],
        "mem_total_mean_bytes": prom["mem_total_mean_bytes"],
    })

out = "runs/summary_table.csv"
os.makedirs("runs", exist_ok=True)
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

print(f"Wrote {out} with {len(rows)} runs")
