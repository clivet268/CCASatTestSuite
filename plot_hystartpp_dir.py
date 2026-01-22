#!/usr/bin/env python3

"""
Use to plot HyStart++ cwnd & RTT vs time for txt logs in a directory, and make a text file that records
state transitions with records of Data.

Usage:
    python3 plot_hystartpp_dir_rounds_with_logs.py input_directory output_directory
"""

import argparse
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt

HSPP_DEACTIVE = 0 # HyStart++ flags 
HSPP_IN_SS = 1
HSPP_IN_CSS = 2

INF_U32 = 0xFFFFFFFF  


# Parsing vars
def parse_hystartpp_log(path: str) -> Dict[str, List[Any]]:
    """
    Parse one HyStart++ txt log into arrays.

    Returns a dict with keys:
      t_s, cwnd, flag,
      rttsample_ctr, curr_min_rtt, last_min_rtt,
      round_ctr, entered_css_at_round, css_baseline_minrtt
    """
    t_us: List[int] = []
    cwnd: List[Optional[int]] = []
    flag: List[Optional[int]] = []
    rttsample_ctr: List[Optional[int]] = []
    curr_min_rtt: List[Optional[int]] = []
    last_min_rtt: List[Optional[int]] = []
    round_ctr: List[Optional[int]] = []
    entered_css_at_round: List[Optional[int]] = []
    css_baseline_minrtt: List[Optional[int]] = []

    cur: Dict[str, Optional[int]] = {
        "t_us": None,
        "cwnd": None,
        "flag": None,
        "rttsample_ctr": None,
        "curr_min_rtt": None,
        "last_min_rtt": None,
        "round_ctr": None,
        "entered_css_at_round": None,
        "css_baseline_minrtt": None,
    }

    # Regexes
    re_now = re.compile(r"now_us:\s*(\d+)")
    re_snd_cwnd = re.compile(r"snd_cwnd:\s*(\d+)")
    re_cwnd = re.compile(r"\bcwnd:\s*(\d+)")
    re_flag = re.compile(r"hspp_flag:\s*(\d+)")
    re_rttctr = re.compile(r"hspp_rttsample_counter:\s*(\d+)")
    re_curr_min = re.compile(r"hspp_current_round_minrtt:\s*(\d+)")
    re_last_min = re.compile(r"hspp_last_round_minrtt:\s*(\d+)")
    re_round_ctr = re.compile(r"hspp_round_counter:\s*(\d+)")
    re_entered_round = re.compile(r"hspp_entered_css_at_round:\s*(\d+)")
    re_css_base = re.compile(r"hspp_css_baseline_minrtt:\s*(\d+)")

    def flush():
        if cur["t_us"] is None:
            return
        t_us.append(cur["t_us"])
        cwnd.append(cur["cwnd"])
        flag.append(cur["flag"])
        rttsample_ctr.append(cur["rttsample_ctr"])
        curr_min_rtt.append(cur["curr_min_rtt"])
        last_min_rtt.append(cur["last_min_rtt"])
        round_ctr.append(cur["round_ctr"])
        entered_css_at_round.append(cur["entered_css_at_round"])
        css_baseline_minrtt.append(cur["css_baseline_minrtt"])
        for k in cur:
            cur[k] = None

    with open(path, "r") as f:
        for raw in f:
            line = raw.rstrip("\n")
            s = line.strip()

            # Start of a new "Line N:" block – flush previous record
            if s.startswith("Line "):
                flush()
                continue

            if not s:
                continue

            if s.startswith("Processing CSV input"):
                continue

            m = re_now.search(s)
            if m:
                cur["t_us"] = int(m.group(1))

            m = re_snd_cwnd.search(s)
            if m:
                cur["cwnd"] = int(m.group(1))
            else:
                m2 = re_cwnd.search(s)
                if m2:
                    cur["cwnd"] = int(m2.group(1))

            m = re_flag.search(s)
            if m:
                cur["flag"] = int(m.group(1))

            m = re_rttctr.search(s)
            if m:
                cur["rttsample_ctr"] = int(m.group(1))

            m = re_curr_min.search(s)
            if m:
                cur["curr_min_rtt"] = int(m.group(1))

            m = re_last_min.search(s)
            if m:
                cur["last_min_rtt"] = int(m.group(1))

            m = re_round_ctr.search(s)
            if m:
                cur["round_ctr"] = int(m.group(1))

            m = re_entered_round.search(s)
            if m:
                cur["entered_css_at_round"] = int(m.group(1))

            m = re_css_base.search(s)
            if m:
                cur["css_baseline_minrtt"] = int(m.group(1))

    flush()

    t_s = [t / 1_000_000.0 for t in t_us]

    return {
        "t_s": t_s,
        "cwnd": cwnd,
        "flag": flag,
        "rttsample_ctr": rttsample_ctr,
        "curr_min_rtt": curr_min_rtt,
        "last_min_rtt": last_min_rtt,
        "round_ctr": round_ctr,
        "entered_css_at_round": entered_css_at_round,
        "css_baseline_minrtt": css_baseline_minrtt,
    }


# state transitions
def find_all_transitions(flags: List[Optional[int]]) -> List[Tuple[int, int, int]]:
    transitions = []
    prev = None
    for i, fl in enumerate(flags):
        if fl is None:
            continue
        if prev is not None and fl != prev:
            transitions.append((i, prev, fl))
        prev = fl
    return transitions

#plot
def plot_one_log(samples: Dict[str, List[Any]],
                 events_ss: List[int],
                 events_css: List[int],
                 events_off: List[int],
                 title: str) -> plt.Figure:
    t_s = samples["t_s"]
    cwnd = samples["cwnd"]
    curr_min = samples["curr_min_rtt"]
    last_min = samples["last_min_rtt"]
    round_ctr = samples["round_ctr"]

    last_vals = [
    (v / 1_000_000.0) if v is not None and v != INF_U32 else float("nan")
    for v in last_min
    ]

    curr_vals = [
    (v / 1_000_000.0) if v is not None and v != INF_U32 else float("nan")
    for v in curr_min
    ]


    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7), sharex=True)

   
    ax1.plot(t_s, cwnd, color="blue", label="cwnd")  # cwnd vs time 

    if events_ss:
        for i in events_ss:
            ax1.axvline(t_s[i], linestyle=":", color="green", alpha=0.6)
        ax1.axvline(t_s[events_ss[0]], linestyle=":", color="green",
                    alpha=0.6, label="Enter SS")

    if events_css:
        for i in events_css:
            ax1.axvline(t_s[i], linestyle="--", color="orange", alpha=0.7)
        ax1.axvline(t_s[events_css[0]], linestyle="--", color="orange",
                    alpha=0.7, label="Enter CSS")

    if events_off:
        for i in events_off:
            ax1.axvline(t_s[i], linestyle="-.", color="red", alpha=0.7)
        ax1.axvline(t_s[events_off[0]], linestyle="-.", color="red",
                    alpha=0.7, label="HyStart++ off")

    
    last_round_seen: Optional[int] = None #Round markers
    for i, rc in enumerate(round_ctr):
        if rc is None:
            continue
        if last_round_seen is not None and rc == last_round_seen:
            continue
        last_round_seen = rc
        if cwnd[i] is None:
            continue
        x = t_s[i]
        y = cwnd[i]
        ax1.plot(x, y, "ko", markersize=3)
        ax1.text(
            x,
            y,
            str(rc),
            ha="center",
            va="center",
            fontsize=7,
            bbox=dict(
                boxstyle="circle,pad=0.2",
                fc="white",
                ec="black",
                lw=0.5,
            ),
        )

    ax1.set_ylabel("cwnd")
    ax1.set_title(title)
    ax1.grid(True, linestyle=":")
    ax1.legend(loc="best")

    ax2.plot(t_s, last_vals, color="purple", label="last_round_minrtt (seconds)") #RTT vs time 
    ax2.plot(t_s, curr_vals, color="green", label="current_round_minrtt (seconds)")

    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("RTT / min RTT (s)")
    ax2.grid(True, linestyle=":")
    ax2.legend(loc="best")

    fig.tight_layout()
    return fig



# Main
def main():
    parser = argparse.ArgumentParser(
        description=(
            "Batch-plot HyStart++ cwnd & RTT vs time for all txt logs in a "
            "directory, marking rounds and writing transition snapshots to "
            "per-log text files."
        )
    )
    parser.add_argument("input_dir", help="Directory containing HyStart++ txt logs")
    parser.add_argument("output_dir", help="Directory to write PNG + txt outputs into")
    args = parser.parse_args()

    in_dir = args.input_dir
    out_dir = args.output_dir
    os.makedirs(out_dir, exist_ok=True)

    txt_files = sorted(f for f in os.listdir(in_dir)
                       if f.lower().endswith(".txt"))
    if not txt_files:
        print("No .txt files found in", in_dir)
        return

    for fname in txt_files:
        in_path = os.path.join(in_dir, fname)
        samples = parse_hystartpp_log(in_path)
        if not samples["t_s"]:
            print(f"{fname}: no samples, skipping.")
            continue

        flags = samples["flag"]
        transitions = find_all_transitions(flags)

        t_s = samples["t_s"]
        round_ctr = samples["round_ctr"]
        last_min = samples["last_min_rtt"]
        curr_min = samples["curr_min_rtt"]
        rtt_ctr = samples["rttsample_ctr"]
        css_base = samples["css_baseline_minrtt"]
        entered_css_round = samples["entered_css_at_round"]

        events_ss: List[int] = []
        events_css: List[int] = []
        events_off: List[int] = []
        log_lines: List[str] = []

        log_lines.append(f"Transitions for {fname}\n")

        for idx, prev, new in transitions:
            ts = t_s[idx]
            rc = round_ctr[idx]
            lmin = last_min[idx]
            cmin = curr_min[idx]
            ctr = rtt_ctr[idx]
            base = css_base[idx]
            ent = entered_css_round[idx]

            header = (f"line={idx}, time={ts:.6f}s, round={rc}, "
                      f"flag {prev}->{new}")

            
            if (prev in (HSPP_DEACTIVE,) and new == HSPP_IN_SS): # SS enter: 0 to 1
                events_ss.append(idx)
                log_lines.append("[SS ENTRY] " + header)
                log_lines.append(
                    f"  rtt_ctr={ctr}, last_min={lmin}, curr_min={cmin}, "
                    f"cssBaselineMinRtt={base}, entered_css_at_round={ent}\n"
                )

            elif (prev == HSPP_IN_CSS and new == HSPP_IN_SS): # abourt CSS: 2 to 1 (resume slow start)
                log_lines.append("[CSS ABORT->SS] " + header)
                
                j = max(idx - 1, 0)
                prev_base = css_base[j]
                prev_curr = curr_min[j]
                cond = (prev_curr is not None and prev_base is not None
                        and prev_curr < prev_base)
                log_lines.append(
                    f"  previous_line={j}, prev_round={round_ctr[j]}, "
                    f"prev_cssBaselineMinRtt={prev_base}, "
                    f"prev_currentRoundMinRTT={prev_curr}"
                )
                log_lines.append(
                    "  condition (currentRoundMinRTT < cssBaselineMinRtt) "
                    f"= {cond}"
                )
                log_lines.append(
                    f"  new cssBaselineMinRtt={base} (should be ~infinity)\n"
                )

            elif (prev == HSPP_IN_SS and new == HSPP_IN_CSS): # CSS enter: 1 to 2
                events_css.append(idx)
                log_lines.append("[CSS ENTRY] " + header)
                log_lines.append(
                    f"  rtt_ctr={ctr}, last_round_minrtt={lmin}, "
                    f"current_round_minrtt={cmin}, "
                    f"cssBaselineMinRtt={base}, "
                    f"entered_css_at_round={ent}\n"
                )

            elif (prev in (HSPP_IN_SS, HSPP_IN_CSS) and new == HSPP_DEACTIVE):  # HyStart++ off
                events_off.append(idx)
                log_lines.append("[HSPP OFF] " + header)
                log_lines.append(
                    f"  rtt_ctr={ctr}, last_min={lmin}, curr_min={cmin}, "
                    f"cssBaselineMinRtt={base}, entered_css_at_round={ent}\n"
                )

        base, _ = os.path.splitext(fname)
        txt_out_path = os.path.join(out_dir, base + "_hspp_transitions.txt")
        with open(txt_out_path, "w") as out_f:
            out_f.write("\n".join(log_lines))
        print(f"{fname}: wrote transitions to {txt_out_path}")

        png_out_path = os.path.join(out_dir, base + "_hspp_rounds.png")
        fig = plot_one_log(
            samples, events_ss, events_css, events_off,
            title=f"HyStart++ cwnd/RTT vs time ({fname})",
        )
        fig.savefig(png_out_path, dpi=150)
        plt.close(fig)
        print(f"{fname}: saved plot to {png_out_path}")


if __name__ == "__main__":
    main()
