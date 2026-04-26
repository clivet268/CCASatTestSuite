#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import re
import pandas as pd

# Exit-time extraction method idea:
# - mlcneta (CUBIC): using the packet-level CSV from the dominant tcp.stream we change the first packet to t=0 
#   and accept the run only if there is a duplicate ACK #3 and its confirming retransmission are both found by t=45s,
#   which is used as the slow-start exit marker. The other servers mlcnetb/mlcnetc/mlcnetd parse the kernel logs.

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

CUBIC_SERVER = "mlcneta"
RUN_DURATION_S = 45.0

FP_RE = re.compile(r"\[FP\]\s*\[(0x[0-9a-fA-F]+)\]")
FW_RE = re.compile(r"\[FRAMEWORK\]\s*\[(\d+),")


def state_re(tag: str) -> re.Pattern:
    return re.compile(rf"\[{re.escape(tag)}\]\s*\[(\d+),(SS|CA)\]")



def parse_log_exit_seconds(log_path: Path, server: str) -> tuple[float, str] | tuple[None, None]:
    """
    Parse SS->CA exit time from framework logs.

    Returns:
        (exit_seconds, chosen_fp) if a valid SS->CA pair is found.
        (None, None) otherwise.
    """
    tag = SERVER_TO_EXIT_TAG.get(server)
    if not tag:
        return None, None

    state_pattern = state_re(tag)
    first_ss_by_fp: dict[str, int] = {}
    fw_count_by_fp: dict[str, int] = {}
    first_ca_by_fp: dict[str, int] = {}

    with log_path.open("r", errors="ignore") as f:
        for line in f:
            fpm = FP_RE.search(line)
            if not fpm:
                continue
            fp = fpm.group(1)

            sm = state_pattern.search(line)
            if sm:
                ts = int(sm.group(1))
                state = sm.group(2)

                if state == "SS":
                    if fp not in first_ss_by_fp:
                        first_ss_by_fp[fp] = ts
                        fw_count_by_fp[fp] = 0
                elif state == "CA":
                    if fp in first_ss_by_fp and fp not in first_ca_by_fp and ts >= first_ss_by_fp[fp]:
                        first_ca_by_fp[fp] = ts
                continue

            if FW_RE.search(line) and fp in first_ss_by_fp and fp not in first_ca_by_fp:
                fw_count_by_fp[fp] = fw_count_by_fp.get(fp, 0) + 1

    candidates: list[tuple[int, int, int, str]] = []
    for fp, ss_ts in first_ss_by_fp.items():
        ca_ts = first_ca_by_fp.get(fp)
        if ca_ts is not None and ca_ts >= ss_ts:
            candidates.append((fw_count_by_fp.get(fp, 0), ss_ts, ca_ts, fp))

    if not candidates:
        return None, None

    _, ss_ts, ca_ts, chosen_fp = max(
        candidates,
        key=lambda x: (x[0], -x[1], -x[2]),
    )
    return (ca_ts - ss_ts) / 1e9, chosen_fp



def parse_cubic_exit_seconds_from_csv(csv_path: Path) -> tuple[dict[str, float | None] | None, str | None]:
    """
    Parse loss-driven slow-start exit time for plain CUBIC from a packet-level CSV.

    A CUBIC run is accepted only if both the first duplicate ACK #3 and a
    retransmission are found by RUN_DURATION_S. 

    Returns (result_dict, None) when we succeed and (None, reason) when failed
    """
    usecols = ["Time", "duplicate_ack", "retransmission"]

    try:
        df = pd.read_csv(csv_path, usecols=usecols)
    except Exception:
        return None, "parse_failed"

    if df.empty:
        return None, "parse_failed"

    df["Time"] = pd.to_numeric(df["Time"], errors="coerce")
    df["duplicate_ack"] = pd.to_numeric(df["duplicate_ack"], errors="coerce")

    valid_time = df["Time"].dropna()
    if valid_time.empty:
        return None, "parse_failed"

    t0 = float(valid_time.iloc[0])
    df["time_from_start"] = df["Time"] - t0

    # Only consider duplicate ACK #3 events that occur within the run window.
    dup3_candidates = df.index[
        df["duplicate_ack"].eq(3) & df["time_from_start"].between(0.0, RUN_DURATION_S, inclusive="both")
    ]

    if len(dup3_candidates) == 0:
        return None, "no_confirmed_dup3_retrans_by_45s"

    for dup3_idx in dup3_candidates:
        dup3_time = float(df.at[int(dup3_idx), "time_from_start"])

        retrans_rows = df.loc[
            (df.index >= int(dup3_idx))
            & df["retransmission"].notna()
            & df["time_from_start"].between(0.0, RUN_DURATION_S, inclusive="both")
        ]

        if retrans_rows.empty:
            continue

        retrans_idx = int(retrans_rows.index[0])
        retrans_time = float(df.at[retrans_idx, "time_from_start"])
        retrans_gap = retrans_time - dup3_time

        return {
            "exit_s": dup3_time,
            "dup_ack3_s": dup3_time,
            "first_retrans_s": retrans_time,
            "retrans_gap_s": retrans_gap,
        }, None

    return None, "no_confirmed_dup3_retrans_by_45s"



def guess_server_from_path(p: Path) -> str | None:
    for part in p.parts:
        if part in SERVER_TO_CCA:
            return part
    return None



def guess_server_from_csv_name(p: Path) -> str | None:
    for server in SERVER_TO_CCA:
        if p.name.startswith(f"{server}_"):
            return server
    return None



def main() -> None:
    ap = argparse.ArgumentParser(
        description=(
            "Compute slow-start exit time per CCA. mlcneta (plain CUBIC) is parsed from "
            "CSV files; mlcnetb/mlcnetc/mlcnetd are parsed from *_45s.log files."
        )
    )
    ap.add_argument("log_root", help="Root directory containing mlcnet*/.../*_45s.log files")
    ap.add_argument(
        "--csv-root",
        help=(
            "Directory containing packet-level CSV files from pcap_to_csv.py. "
            "Used for mlcneta only; expected names like mlcneta_<timestamp>_45s.csv."
        ),
    )
    ap.add_argument("--out", default="exit_times.csv", help="Output CSV")
    ap.add_argument(
        "--debug",
        action="store_true",
        help="Print the chosen exit marker for each parsed file",
    )
    args = ap.parse_args()

    log_root = Path(args.log_root)
    logs = sorted(log_root.rglob("*_45s.log"))
    if not logs:
        raise SystemExit(f"No *_45s.log files found under {log_root}")

    cubic_csvs: list[Path] = []
    if args.csv_root:
        csv_root = Path(args.csv_root)
        cubic_csvs = sorted(csv_root.rglob(f"{CUBIC_SERVER}_*_45s.csv"))
        if not cubic_csvs:
            print(f"Warning: No {CUBIC_SERVER}_*_45s.csv files found under {csv_root}")

    rows: list[dict[str, object]] = []
    counts = {server: {"files_seen": 0, "runs_used": 0, "runs_skipped": 0} for server in SERVER_TO_CCA}
    skipped_reasons = {
        server: {
            "parse_failed": 0,
            "no_confirmed_dup3_retrans_by_45s": 0,
        }
        for server in SERVER_TO_CCA
    }

    # Parse CUBIC from CSVs when we can.
    if cubic_csvs:
        counts[CUBIC_SERVER]["files_seen"] = len(cubic_csvs)
        for csv_path in cubic_csvs:
            server = guess_server_from_csv_name(csv_path)
            if server != CUBIC_SERVER:
                continue

            result, reason = parse_cubic_exit_seconds_from_csv(csv_path)
            if result is None:
                counts[server]["runs_skipped"] += 1
                skipped_reasons[server][reason or "parse_failed"] += 1
                if args.debug:
                    if reason == "no_confirmed_dup3_retrans_by_45s":
                        print(f"Skipping {csv_path.name}: no dupACK3 + retransmission pair by {RUN_DURATION_S:.0f}s")
                    else:
                        print(f"Skipping {csv_path.name}: could not parse CUBIC CSV")
                continue

            exit_s = float(result["exit_s"])

            counts[server]["runs_used"] += 1
            rows.append(
                {
                    "server": server,
                    "cca": SERVER_TO_CCA[server],
                    "source_kind": "csv",
                    "source_file": str(csv_path),
                    "method": "dup_ack_3_confirmed_by_retrans",
                    "chosen_fp": None,
                    "exit_s": exit_s,
                    "dup_ack3_s": result["dup_ack3_s"],
                    "first_retrans_s": result["first_retrans_s"],
                    "retrans_gap_s": result["retrans_gap_s"],
                }
            )

            if args.debug:
                retrans_str = (
                    f" retrans={result['first_retrans_s']:.6f}s gap={result['retrans_gap_s']:.6f}s"
                    if result["first_retrans_s"] is not None and result["retrans_gap_s"] is not None
                    else " retrans=None"
                )
                print(
                    f"{SERVER_TO_CCA[server]:<14} "
                    f"exit_s={exit_s:.6f} "
                    f"dup3={result['dup_ack3_s']:.6f}s"
                    f"{retrans_str} "
                    f"csv={csv_path.name}"
                )

    # Parse remaining CCAs from logs. If no CSV directory is provided, CUBIC also uses kernel logs.
    for log_path in logs:
        server = guess_server_from_path(log_path)
        if not server:
            continue
        if cubic_csvs and server == CUBIC_SERVER:
            continue

        counts[server]["files_seen"] += 1
        exit_s, chosen_fp = parse_log_exit_seconds(log_path, server)
        if exit_s is None:
            counts[server]["runs_skipped"] += 1
            skipped_reasons[server]["parse_failed"] += 1
            if args.debug:
                print(f"Skipping {log_path.name}: could not extract SS->CA transition")
            continue

        counts[server]["runs_used"] += 1
        rows.append(
            {
                "server": server,
                "cca": SERVER_TO_CCA[server],
                "source_kind": "log",
                "source_file": str(log_path),
                "method": "log_ss_to_ca",
                "chosen_fp": chosen_fp,
                "exit_s": float(exit_s),
                "dup_ack3_s": None,
                "first_retrans_s": None,
                "retrans_gap_s": None,
            }
        )

        if args.debug:
            print(
                f"{SERVER_TO_CCA[server]:<14} "
                f"FP={chosen_fp} "
                f"exit_s={exit_s:.6f} "
                f"log={log_path.name}"
            )

    df = pd.DataFrame(rows)
    df.to_csv(args.out, index=False)
    print(f"Wrote {len(df)} exit samples -> {args.out}")

    summary_rows = []
    for server, cca in SERVER_TO_CCA.items():
        files_seen = counts[server]["files_seen"]
        runs_used = counts[server]["runs_used"]
        runs_skipped = counts[server]["runs_skipped"]
        sub = df[df["server"] == server]["exit_s"] if not df.empty else pd.Series(dtype=float)

        summary_rows.append(
            {
                "server": server,
                "cca": cca,
                "files_seen": files_seen,
                "runs_used": runs_used,
                "runs_skipped": runs_skipped,
                "skipped_parse_failed": skipped_reasons[server]["parse_failed"],
                "skipped_no_confirmed_dup3_retrans_by_45s": skipped_reasons[server]["no_confirmed_dup3_retrans_by_45s"],
                "mean_s": sub.mean() if not sub.empty else None,
                "median_s": sub.median() if not sub.empty else None,
                "std_s": sub.std(ddof=1) if len(sub) > 1 else None,
            }
        )

    summary_df = pd.DataFrame(summary_rows)
    print("\nExit summary:")
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
