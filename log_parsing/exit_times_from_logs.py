#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import re
import numpy as np
import pandas as pd

SERVER_TO_CCA = {
    "mlcneta": "Cubic",
    "mlcnetb": "Cubic_hystart",
    "mlcnetc": "Cubic_hspp",
    "mlcnetd": "Cubic_search",
}

SERVER_TO_EXIT_TAG = {
    "mlcneta": "CUB",
    "mlcnetb": "HS",
    "mlcnetc": "HSPP",
    "mlcnetd": "SEARCH",
}


FP_RE = re.compile(r"\[FP\]\s*\[(0x[0-9a-fA-F]+)\]") # compile regexes to extract timestamps:
FW_RE = re.compile(r"\[FRAMEWORK\]\s*\[(\d+),")
CA_RE = re.compile(r"\[CA\]\s*\[(\d+)\]")
def ca_re(tag: str) -> re.Pattern:
    return re.compile(rf"\[{re.escape(tag)}\]\s*\[(\d+),CA\]")

def parse_exit_seconds(log_path: Path, server: str) -> float | None:
    tag = SERVER_TO_EXIT_TAG.get(server)
    if not tag:
        return None
    CA_RE = ca_re(tag)

    # Track per-flow timestamps so we can pair t0 + CA on same flow
    t0_by_fp: dict[str, int] = {}
    ca_by_fp: dict[str, int] = {}

    with log_path.open("r", errors="ignore") as f:
        for line in f:
            fpm = FP_RE.search(line)
            if not fpm:
                continue
            fp = fpm.group(1)

            # first framework timestamp for this FP
            if fp not in t0_by_fp:
                m0 = FW_RE.search(line)
                if m0:
                    t0_by_fp[fp] = int(m0.group(1))

            # first CA timestamp for this FP
            if fp not in ca_by_fp:
                me = CA_RE.search(line)
                if me:
                    ca_by_fp[fp] = int(me.group(1))

            # early stop if we already have a matched FP
            if fp in t0_by_fp and fp in ca_by_fp:
                t0 = t0_by_fp[fp]
                ca = ca_by_fp[fp]
                if ca >= t0:
                    return (ca - t0) / 1e9

    # If we didn't find a matched FP, new framework timestamp, or CA timestamp, we can still try to guess using any timestamps in the log:
    t0_any = None
    ca_any = None
    with log_path.open("r", errors="ignore") as f:
        for line in f:
            if t0_any is None:
                m0 = FW_RE.search(line)
                if m0:
                    t0_any = int(m0.group(1))
            if ca_any is None:
                me = CA_RE.search(line)
                if me:
                    ca_any = int(me.group(1))
            if t0_any is not None and ca_any is not None:
                break
    if t0_any is None or ca_any is None or ca_any < t0_any:
        return None
    return (ca_any - t0_any) / 1e9

def guess_server_from_path(p: Path) -> str | None:
    # expects /mlcneta/... etc somewhere in path
    for part in p.parts:
        if part in SERVER_TO_CCA:
            return part
    return None

def main():
    ap = argparse.ArgumentParser(description="Compute SS->CA exit time (seconds) per CCA from *_45s.log files.")
    ap.add_argument("log_root", help="Root directory containing mlcnet*/.../*.log")
    ap.add_argument("--out", default="exit_times.csv", help="Output CSV")
    args = ap.parse_args()

    log_root = Path(args.log_root)
    logs = list(log_root.rglob("*_45s.log"))
    if not logs:
        raise SystemExit(f"No *_45s.log files found under {log_root}")

    rows = []
    for lp in logs:
        server = guess_server_from_path(lp)
        if not server:
            continue
        exit_s = parse_exit_seconds(lp, server)
        if exit_s is None:
            continue
        rows.append({
            "server": server,
            "cca": SERVER_TO_CCA[server],
            "log": str(lp),
            "exit_s": float(exit_s),
        })

    df = pd.DataFrame(rows)
    df.to_csv(args.out, index=False)
    print(f"Wrote {len(df)} exit samples -> {args.out}")

    if df.empty:
        print("No exit times parsed.")
        return

    summary = (df.groupby(["server", "cca"])["exit_s"]
               .agg(n="count", mean_s="mean", median_s="median", std_s="std")
               .reset_index())
    print("\nExit summary:")
    print(summary.to_string(index=False))

if __name__ == "__main__":
    main()