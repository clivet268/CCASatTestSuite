#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

SERVER_TO_CCA: Dict[str, str] = {
    "mlcneta": "Cubic",
    "mlcnetb": "Cubic_hystart",
    "mlcnetc": "Cubic_hspp",
    "mlcnetd": "Cubic_search",
}

SERVER_ORDER = ["mlcneta", "mlcnetb", "mlcnetc", "mlcnetd"]

SERVER_TO_SENDER_IP: Dict[str, str] = {
    "mlcneta": "184.62.125.3",
    "mlcnetb": "184.62.125.3",
    "mlcnetc": "184.62.125.3",
    "mlcnetd": "184.62.125.3",
}

#interval_s: float = 0.05,
def calculate_throughput_bins(
    csv_path: Path,
    server: str,
    interval_s: float = 0.05,
    duration_s: float = 45.0,
) -> np.ndarray:
    """
    Calculate pcap-derived throughput (Mbps) in fixed time bins.

    Time is shifted so t=0 at the first sender packet in CSV.
    """
    df = pd.read_csv(csv_path)

    sender_ip = SERVER_TO_SENDER_IP.get(server)
    if not sender_ip:
        print(f"Warning: No sender IP configured for server {server}")
        return np.full(int(np.ceil(duration_s / interval_s)), np.nan)

    length_col = None
    for candidate in ["Ack number"]:
        if candidate in df.columns:
            length_col = candidate
            break

    if length_col is None:
        print(f"Warning: No usable length column found in {csv_path}")
        return np.full(int(np.ceil(duration_s / interval_s)), np.nan)

    df_sender = df[df["Source"] == sender_ip].copy()
    df_sender["Time"] = pd.to_numeric(df_sender["Time"], errors="coerce")
    df_sender[length_col] = pd.to_numeric(df_sender[length_col], errors="coerce")
    df_sender = df_sender.dropna(subset=["Time", length_col]).sort_values("Time")

    if df_sender.empty:
        print(f"Warning: No valid sender packets in {csv_path}")
        return np.full(int(np.ceil(duration_s / interval_s)), np.nan)

    t0 = df_sender["Time"].iloc[0]
    df_sender["Time"] = df_sender["Time"] - t0

    df_sender = df_sender[(df_sender["Time"] >= 0) & (df_sender["Time"] < duration_s)]
    if df_sender.empty:
        return np.full(int(np.ceil(duration_s / interval_s)), np.nan)

    num_bins = int(np.ceil(duration_s / interval_s))
    throughputs = np.full(num_bins, np.nan, dtype=float)

    for bin_idx in range(num_bins):
        bin_start = bin_idx * interval_s
        bin_end = (bin_idx + 1) * interval_s

        bin_packets = df_sender[
            (df_sender["Time"] >= bin_start) &
            (df_sender["Time"] < bin_end)
        ]
        ##print(bin_packets)

        if not bin_packets.empty:
        #TODO here we would need tofiler if ha binbacke had an ACK and hen record is lengh
            ini = -1;
            #bin_packets.sort_values(by='') 
            #print(length_col)
            #print(bin_packets[length_col])
            #print(bin_packets[length_col].dtype)
            #print(bin_packets[length_col].tolist())
            #print(bin_packets[length_col].values.dtype)
            #print(bin_packets[length_col].values.tolist())
            #print()
            #print(bin_packets[length_col])
            #print()
            whaever = bin_packets[length_col].values.tolist()
            if len(whaever) > 1:
                sumbin = whaever[-1] - whaever[0]
            else:
                sumbin = 0
            
            #for packe in range(len(bin_packets)):
            #    if(ini == -1):
                    
            #total_mbits = bin_packets[length_col].sum() * 8 * 1e-6
            total_mbits = sumbin * 8 * 1e-6
            throughputs[bin_idx] = total_mbits / interval_s

    return throughputs


def smooth_nanaware(x: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """
    Moving-average smoothing that ignores NaNs.
    """
    x = x.astype(float)
    valid = np.isfinite(x).astype(float)
    x_filled = np.where(np.isfinite(x), x, 0.0)

    num = np.convolve(x_filled, kernel, mode="same")
    den = np.convolve(valid, kernel, mode="same")

    return np.divide(num, den, out=np.full_like(num, np.nan), where=den > 0)


def run_exit_time_script(log_root: Path, exit_script: Path, exit_csv_out: Path) -> pd.DataFrame:
    """
    Call exit_times_from_logs.py, let it print its terminal summary,
    then read the CSV.
    """
    command = [
        sys.executable,
        str(exit_script),
        str(log_root),
        "--out",
        str(exit_csv_out),
    ]
    print("Running exit-time script:")
    print("  " + " ".join(command))
    subprocess.run(command, check=True)

    if not exit_csv_out.exists():
        raise FileNotFoundError(f"Exit CSV was not created: {exit_csv_out}")

    df = pd.read_csv(exit_csv_out)
    if df.empty:
        print("Warning: exit time CSV is empty.")
    return df


def build_exit_time_map(exit_df: pd.DataFrame) -> Dict[str, float]:
    """
    Return mean exit time in seconds per server.
    """
    if exit_df.empty:
        return {}

    required = {"server", "exit_s"}
    if not required.issubset(exit_df.columns):
        raise ValueError(f"Exit CSV missing required columns: {required}")

    grouped = exit_df.groupby("server", as_index=False)["exit_s"].mean()

    exit_map: Dict[str, float] = {}
    for _, row in grouped.iterrows():
        exit_map[str(row["server"])] = float(row["exit_s"])
    return exit_map
    
# Source - https://stackoverflow.com/a/7968690
# Posted by Yann, modified by community. See post 'Timeline' for change history
# Retrieved 2026-04-12, License - CC BY-SA 3.0
def adjustFigAspect(fig,aspect=1):
    '''
    Adjust the subplot parameters so that the figure has the correct
    aspect ratio.
    '''
    xsize,ysize = fig.get_size_inches()
    minsize = min(xsize,ysize)
    xlim = .4*minsize/xsize
    ylim = .4*minsize/ysize
    if aspect < 1:
        xlim *= aspect
    else:
        ylim /= aspect
    fig.subplots_adjust(left=.5-xlim,
                        right=.5+xlim,
                        bottom=.5-ylim,
                        top=.5+ylim)

def main():
    ap = argparse.ArgumentParser(
        description=(
            "Plot average pcap-derived throughput vs time with 95% CI, and "
            "overlay mean SS->CA exit time per congestion control as a dashed "
            "vertical line in the matching color."
        )
    )
    ap.add_argument("csv_dir", help="Directory containing throughput CSV files")
    ap.add_argument("log_root", help="Root directory containing mlcnet*/.../*_45s.log files")
    ap.add_argument("out", help="Output PNG filename")
    ap.add_argument("title", help="Plot title (quote if it has spaces)")
    ap.add_argument("interval", type=float, help="Bin size in seconds (like, 0.05 for 50ms)")
    ap.add_argument("duration", type=float, help="Total duration in seconds")
    ap.add_argument(
        "--exit-script",
        default="exit_times_from_logs.py",
        help="Path to exit_times_from_logs.py (default: exit_times_from_logs.py in current directory)",
    )
    ap.add_argument(
        "--exit-csv-out",
        default="exit_times.csv",
        help="Where to write the generated exit-time CSV (default: exit_times.csv)",
    )
    args = ap.parse_args()

    csv_dir = Path(args.csv_dir)
    log_root = Path(args.log_root)
    exit_script = Path(args.exit_script)
    exit_csv_out = Path(args.exit_csv_out)

    if not csv_dir.exists():
        raise SystemExit(f"CSV directory not found: {csv_dir}")
    if not log_root.exists():
        raise SystemExit(f"Log root not found: {log_root}")
    if not exit_script.exists():
        raise SystemExit(f"Exit-time script not found: {exit_script}")

    csv_files = list(csv_dir.glob("*.csv"))
    if not csv_files:
        raise SystemExit(f"No CSV files found in {csv_dir}")

    exit_df = run_exit_time_script(log_root, exit_script, exit_csv_out)
    exit_time_map = build_exit_time_map(exit_df)

    server_runs: Dict[str, List[np.ndarray]] = {}

    for csv_file in csv_files:
        filename = csv_file.name
        if "_" not in filename:
            print(f"Warning: Skipping {filename} - cannot determine server")
            continue

        server = filename.split("_")[0]
        if server not in SERVER_TO_CCA:
            print(f"Warning: Unknown server {server} in {filename}")
            continue

        print(f"Processing {filename} for server {server}")
        throughputs = calculate_throughput_bins(csv_file, server, args.interval, args.duration)
        server_runs.setdefault(server, []).append(throughputs)
        #try:
        #except Exception as e:
        #    print(e)
        #    print(f"Error processing {csv_file}: {e}")

    if not server_runs:
        raise SystemExit("No valid CSV files processed")

    num_bins = int(np.ceil(args.duration / args.interval))
    time_axis = np.arange(num_bins) * args.interval

    fig, ax = plt.subplots(figsize=(12, 8))
    colors = ["blue", "orange", "green", "red"]

    kernel_bins = 25
    kernel = np.ones(kernel_bins) / kernel_bins

    plotted_servers = [s for s in SERVER_ORDER if s in server_runs]

    for i, server in enumerate(plotted_servers):
        runs = server_runs[server]
        if not runs:
            continue

        runs_array = np.vstack(runs)
        runs_smoothed = np.vstack([smooth_nanaware(r, kernel) for r in runs_array])

        means = np.nanmean(runs_smoothed, axis=0)

        if runs_smoothed.shape[0] > 1:
            stds = np.nanstd(runs_smoothed, axis=0, ddof=1)
            n_eff = np.sum(np.isfinite(runs_smoothed), axis=0)
            ses = stds / np.sqrt(n_eff)
            cis = 1.96 * ses
        else:
            cis = np.zeros_like(means)

        color = colors[i % len(colors)]
        cca_name = SERVER_TO_CCA.get(server, server)

        ax.fill_between(time_axis, means - cis, means + cis, alpha=0.2, color=color, linewidth=0)
        ax.plot(time_axis, means, color=color, linewidth=2, label=f"{server} ({cca_name}) n={len(runs)}")

        exit_time_s = exit_time_map.get(server)
        if exit_time_s is not None and np.isfinite(exit_time_s):
            ax.axvline(
                exit_time_s,
                color=color,
                linestyle="--",
                linewidth=1.8,
                alpha=0.9,
                label=f"{cca_name} avg exit ({exit_time_s:.2f}s)",
            )

    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Goodput (Mb/s)")
    ax.set_title(args.title)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.rcParams.update({'font.size': 15.0})
    plt.rcParams.update({'font.weight' : 'bold'})
    plt.rcParams.update({'lines.linewidth' : 6.0})

    plt.tight_layout()
    plt.ylim(0, 300)
    fig = plt.figure()
    adjustFigAspect(fig,aspect=.75)
    
    fig.savefig(args.out, dpi=200, bbox_inches="tight")
    print(f"Saved plot to {args.out}")

    print("\nSummary:")
    for server in plotted_servers:
        print(f"{server}: {len(server_runs[server])} runs processed")
        if server in exit_time_map:
            print(f"  mean exit time: {exit_time_map[server]:.6f}s")


if __name__ == "__main__":
    main()
