from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import yaml


@dataclass
class QueryDef:
    name: str
    query: str


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Export Prometheus range queries to CSV")
    p.add_argument("--prom-url", default=os.environ.get("PROM_URL", "http://localhost:9090"))
    p.add_argument("--run-id", required=True)
    p.add_argument("--start", required=True, help="RFC3339 or unix timestamp")
    p.add_argument("--end", required=True, help="RFC3339 or unix timestamp")
    p.add_argument("--step", type=int, default=15, help="step in seconds")
    p.add_argument("--query-file", required=True, help="YAML file mapping metric_name -> {query: ...}")
    return p.parse_args()


def load_queries(path: str) -> list[QueryDef]:
    data = yaml.safe_load(Path(path).read_text())
    out: list[QueryDef] = []
    for name, obj in data.items():
        q = obj.get("query") if isinstance(obj, dict) else None
        if not q:
            raise ValueError(f"Missing query for {name}")
        out.append(QueryDef(name=name, query=q.strip()))
    return out


def prom_query_range(prom_url: str, query: str, start: str, end: str, step: int) -> dict[str, Any]:
    r = requests.get(
        f"{prom_url.rstrip('/')}/api/v1/query_range",
        params={"query": query, "start": start, "end": end, "step": step},
        timeout=60,
    )
    r.raise_for_status()
    payload = r.json()
    if payload.get("status") != "success":
        raise RuntimeError(f"Prometheus query failed: {payload}")
    return payload


def to_dataframe(result: dict[str, Any]) -> pd.DataFrame:
    # result is one vector per labelset; convert to long format
    rows = []
    for series in result.get("data", {}).get("result", []):
        metric = series.get("metric", {})
        for ts, val in series.get("values", []):
            rows.append({"ts": float(ts), "value": float(val), **metric})
    df = pd.DataFrame(rows)
    if not df.empty:
        df["datetime"] = pd.to_datetime(df["ts"], unit="s", utc=True)
    return df


def main() -> None:
    args = parse_args()
    queries = load_queries(args.query_file)

    out_dir = Path("data/raw") / args.run_id / "prometheus"
    out_dir.mkdir(parents=True, exist_ok=True)

    for q in queries:
        payload = prom_query_range(args.prom_url, q.query, args.start, args.end, args.step)
        df = to_dataframe(payload)
        out_path = out_dir / f"{q.name}.csv"
        df.to_csv(out_path, index=False)
        print(f"wrote {out_path} ({len(df)} rows)")


if __name__ == "__main__":
    main()
