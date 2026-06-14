import csv, json, math, statistics, sys, os

# usage: python3 summarize_run.py runs/<run_name>
run_dir = sys.argv[1].rstrip("/")

def read_meta(path):
    meta = {}
    with open(path) as f:
        for line in f:
            line=line.strip()
            if not line or "=" not in line: 
                continue
            k,v = line.split("=",1)
            meta[k]=v
    for k in ("start_epoch","end_epoch","export_start_epoch","export_end_epoch","step"):
        if k in meta:
            meta[k]=int(meta[k])
    return meta

def percentile(sorted_vals, p):
    if not sorted_vals:
        return None
    k = (len(sorted_vals)-1) * p
    f = math.floor(k); c = math.ceil(k)
    if f == c:
        return sorted_vals[int(k)]
    return sorted_vals[f] + (sorted_vals[c]-sorted_vals[f])*(k-f)

meta = read_meta(os.path.join(run_dir, "meta.txt"))
start = meta["start_epoch"]
end = meta["end_epoch"]
duration = end - start

# ---- hey.csv summary ----
lat = []
status_counts = {}
total = 0

with open(os.path.join(run_dir, "hey.csv")) as f:
    r = csv.DictReader(f)
    for row in r:
        total += 1
        try:
            lat.append(float(row["response-time"]))
        except Exception:
            pass
        sc = row.get("status-code","")
        status_counts[sc] = status_counts.get(sc, 0) + 1

lat.sort()
ok = status_counts.get("200", 0) + status_counts.get("302", 0)  # treat 302 as ok for web apps
errors = total - ok

hey_summary = {
    "requests": total,
    "duration_seconds": duration,
    "arrival_rate_rps": (total / duration) if duration > 0 else None,
    "status_counts": status_counts,
    "error_fraction": (errors / total) if total else None,
    "latency_seconds": {
        "mean": (sum(lat)/len(lat)) if lat else None,
        "median": percentile(lat, 0.50),
        "p90": percentile(lat, 0.90),
        "p95": percentile(lat, 0.95),
        "p99": percentile(lat, 0.99),
        "min": lat[0] if lat else None,
        "max": lat[-1] if lat else None,
    }
}

# ---- Prometheus summary from CSV (filter to run window only) ----
def summarize_prom_csv(path):
    with open(path) as f:
        r = csv.reader(f)
        header = next(r)
        # header[0] = timestamp
        cols = header[1:]
        sums = [0.0] * len(cols)
        counts = [0] * len(cols)
        for row in r:
            ts = int(float(row[0]))
            if ts < start or ts > end:
                continue
            for i, v in enumerate(row[1:]):
                if v == "" or v is None:
                    continue
                try:
                    sums[i] += float(v)
                    counts[i] += 1
                except ValueError:
                    pass
        means = {}
        for i, name in enumerate(cols):
            means[name] = (sums[i]/counts[i]) if counts[i] else None
        return means

cpu_by_pod_means = summarize_prom_csv(os.path.join(run_dir, "cpu_by_pod.csv"))
mem_by_pod_means = summarize_prom_csv(os.path.join(run_dir, "mem_by_pod.csv"))
cpu_total_mean = summarize_prom_csv(os.path.join(run_dir, "cpu_total.csv")).get("series")
mem_total_mean = summarize_prom_csv(os.path.join(run_dir, "mem_total.csv")).get("series")

summary = {
    "run": {
        "name": meta.get("run_name"),
        "url": meta.get("url"),
        "concurrency": meta.get("concurrency"),
        "q_per_worker": meta.get("q_per_worker"),
        "start_epoch": start,
        "end_epoch": end,
    },
    "hey": hey_summary,
    "prometheus": {
        "cpu_total_mean_cores": cpu_total_mean,
        "mem_total_mean_bytes": mem_total_mean,
        "cpu_mean_cores_by_pod": cpu_by_pod_means,
        "mem_mean_bytes_by_pod": mem_by_pod_means,
    }
}

out_path = os.path.join(run_dir, "summary.json")
with open(out_path, "w") as f:
    json.dump(summary, f, indent=2, sort_keys=True)

print(f"Wrote {out_path}")
print(f"Arrival rate (rps): {hey_summary['arrival_rate_rps']:.3f}")
print(f"Latency mean/p95/p99 (s): {hey_summary['latency_seconds']['mean']:.4f} / {hey_summary['latency_seconds']['p95']:.4f} / {hey_summary['latency_seconds']['p99']:.4f}")
print(f"CPU total mean (cores): {cpu_total_mean}")
