#!/usr/bin/env python3

"""
Use to plot HyStart++ cwnd & RTT vs time for txt logs in a directory, and make a text file that records
state transitions with records of data.

Usage:
    python3 plot_hystartpp_dir_rounds_with_logs.py input_directory output_directory
"""

import argparse
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt

HSPP_DEACTIVE = 0 #HyStart++ flags
HSPP_IN_SS = 1
HSPP_IN_CSS = 2

INF_U32 = 0xFFFFFFFF


MIN_RTT_THRESH_US = 4000 #RFC 9406 defaults (microseconds)
MAX_RTT_THRESH_US = 16000
MIN_RTT_DIVISOR = 8


# Parsing vars
def parse_hystartpp_log(path: str) -> Dict[str, List[Any]]:
    """
    Parse one HyStart++ txt log into arrays.

    Returns a dict with keys:
      t_s, line_no, cwnd, flag,
      rttsample_ctr, curr_min_rtt, last_min_rtt,
      round_ctr, entered_css_at_round, css_baseline_minrtt
    """
    t_us: List[int] = []
    line_no: List[Optional[int]] = []
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
        "line_no": None,
        "cwnd": None,
        "flag": None,
        "rttsample_ctr": None,
        "curr_min_rtt": None,
        "last_min_rtt": None,
        "round_ctr": None,
        "entered_css_at_round": None,
        "css_baseline_minrtt": None,
    }

    re_linehdr = re.compile(r"Line\s+(\d+):")
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
        line_no.append(cur["line_no"])
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

            if s.startswith("Line "):
                flush()
                mline = re_linehdr.match(s)
                if mline:
                    cur["line_no"] = int(mline.group(1))
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
        "line_no": line_no,
        "cwnd": cwnd,
        "flag": flag,
        "rttsample_ctr": rttsample_ctr,
        "curr_min_rtt": curr_min_rtt,
        "last_min_rtt": last_min_rtt,
        "round_ctr": round_ctr,
        "entered_css_at_round": entered_css_at_round,
        "css_baseline_minrtt": css_baseline_minrtt,
    }

def find_all_transitions(flags: List[Optional[int]]) -> List[Tuple[int, int, int]]: # state transitions
    transitions = []
    prev = None
    for i, fl in enumerate(flags):
        if fl is None:
            continue
        if prev is not None and fl != prev:
            transitions.append((i, prev, fl))
        prev = fl
    return transitions


def compute_state_durations(t_s: List[float], flags: List[Optional[int]]) -> Dict[int, float]: # state duration 
    """
    Compute time spent in each hspp_flag state by integrating between samples.
    Returns seconds in each state (keyed by flag value).
    """
    dur: Dict[int, float] = {HSPP_DEACTIVE: 0.0, HSPP_IN_SS: 0.0, HSPP_IN_CSS: 0.0}
    if not t_s or len(t_s) != len(flags):
        return dur

    prev_t: Optional[float] = None
    prev_f: Optional[int] = None

    for i in range(len(t_s)):
        cur_t = t_s[i]
        cur_f = flags[i]

        if prev_t is not None and prev_f is not None and cur_t is not None:
            dt = cur_t - prev_t
            if dt >= 0 and prev_f in dur:
                dur[prev_f] += dt

        prev_t = cur_t
        prev_f = cur_f

    return dur


def clamp(x: int, lo: int, hi: int) -> int: # RTTThresh helpers
    return max(lo, min(x, hi))


def compute_rtt_thresh_us(last_round_minrtt_us: Optional[int]) -> Optional[int]:
    """
    RTTThresh = max(4ms, min(lastRoundMinRTT/8, 16ms))
    In microseconds: max(4000, min(last/8, 16000)).
    Uses integer division (floor) like the kernel bitshift.
    """
    if last_round_minrtt_us is None or last_round_minrtt_us == INF_U32:
        return None
    raw = last_round_minrtt_us // MIN_RTT_DIVISOR
    return clamp(raw, MIN_RTT_THRESH_US, MAX_RTT_THRESH_US)


def plot_one_log(samples: Dict[str, List[Any]], #plot
                 events_ss: List[int],
                 events_css: List[int],
                 events_off: List[int],
                 title: str) -> plt.Figure:
    t_s = samples["t_s"]
    cwnd = samples["cwnd"]
    curr_min = samples["curr_min_rtt"]
    last_min = samples["last_min_rtt"]
    round_ctr = samples["round_ctr"]
    baseline_min = samples["css_baseline_minrtt"]
    flags = samples.get("flag", [])


   #conversion to seconds
    last_vals = [
        (v / 1_000_000.0) if v is not None and v != INF_U32 else float("nan")
        for v in last_min
    ]

    curr_vals = [
        (v / 1_000_000.0) if v is not None and v != INF_U32 else float("nan")
        for v in curr_min
    ]

    baseline_vals = []
    for i, v in enumerate(baseline_min):
        if flags[i] != HSPP_IN_CSS:
            baseline_vals.append(float("nan"))
        elif v is None or v == INF_U32:
            baseline_vals.append(float("nan"))
        else:
            baseline_vals.append(v / 1_000_000.0)



    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7), sharex=True)

    ax1.plot(t_s, cwnd, color="blue", label="cwnd")  # cwnd vs time

    if events_ss:
        for i in events_ss:
            ax1.axvline(t_s[i], linestyle=":", color="green", alpha=0.6)
        ax1.axvline(t_s[events_ss[0]], linestyle=":", color="green",
                    alpha=0.6, label="SS (re-entry)")

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

   
    exit_css_idxs: List[int] = []
    prev_flag: Optional[int] = None
    for i, fl in enumerate(flags):
        if fl is None:
            continue
        if prev_flag is not None and prev_flag == HSPP_IN_CSS and fl == HSPP_IN_SS:
            exit_css_idxs.append(i)
        prev_flag = fl

    if exit_css_idxs:
        for i in exit_css_idxs:
            ax1.axvline(t_s[i], linestyle=":", color="green", alpha=0.9)

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
    ax1.grid(False)
    ax1.legend(loc="lower right")

    ax2.plot(t_s, last_vals, color="purple", label="last_round_minrtt (seconds)")  # RTT vs time

    bt = []
    bv = []
    last = None
    for i, v in enumerate(baseline_vals):
        if v != last:
            bt.append(t_s[i])
            bv.append(v)
            last = v

    ax2.plot(
    t_s,
    baseline_vals,
    color="red",
    linewidth=2.0,
    linestyle="--",
    zorder=5,
    label="hspp_css_baseline_minrtt (seconds)"
    )



    ax2.plot(
        t_s,
        curr_vals,
        color="green",
        linewidth=1.5,
        zorder=3,
        label="current_round_minrtt (seconds)"
    )

    
    for idx in events_css: # CSS baseline RTT when CSS is entered
        if idx >= len(t_s):
            continue
        base = baseline_min[idx]
        if base is None or base == INF_U32:
            continue
        ax2.plot(
            t_s[idx],
            base / 1_000_000.0,
            marker="o",
            markersize=5,
            markerfacecolor="orange",
            markeredgecolor="black",
            zorder=4
        )

    if events_css:
        ax2.plot(
            [],
            [],
            marker="o",
            linestyle="None",
            markerfacecolor="orange",
            markeredgecolor="black",
            label="CSS baseline RTT"
        )

    round_change_idxs = []   
    last_round_seen2 = None
    for i, rc in enumerate(round_ctr): #round marker for rtt diagram
       if rc is None:
         continue
       if last_round_seen2 is None:
         last_round_seen2 = rc
         continue
       if rc != last_round_seen2:
          round_change_idxs.append(i)
          last_round_seen2 = rc

    for i in round_change_idxs:
        ax2.axvline(
        t_s[i],
        color="grey",
        linestyle="--",
        linewidth=0.8,
        alpha=0.4
    )

    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("RTT / min RTT (s)")
    ax2.grid(False)
    ax2.legend(loc="lower right")

    ax1.set_ylim(bottom=0) # axes 
    ax2.set_ylim(bottom=0)
    ax1.set_xlim(left=0)

    fig.tight_layout()
    return fig


# Main
def main():
    parser = argparse.ArgumentParser(
        description=(
            "plot HyStart++ cwnd & RTT vs time for all logs in a "
            "directory, highlighting rounds and writing transition snapshots to "
            "text files."
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
        line_no = samples["line_no"]
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

        log_lines.append("/* {RFC9406_L253} */") # RFC 9406 constants 
        log_lines.append("#define HSPP_MIN_RTT_THRESH\t(4000U)\t\t/*  4 ms\t*/")
        log_lines.append("#define HSPP_MAX_RTT_THRESH\t(16000U)\t/* 16 ms\t*/")
        log_lines.append("#define HSPP_CSS_MIN_RTT_DIV\t3\t\t/* RTT threshold is computed as RTT / (2^HSPP_CSS_MIN_RTT_DIV)\t*/")
        log_lines.append("#define HSPP_N_RTT_SAMPLE\t8\t\t/* Number of RTTs in CSS to determine whether the exit from SS was premature\t*/")
        log_lines.append("#define HSPP_CSS_GROWTH_DIV\t4\t\t/* For less aggressive growth, cwnd increase is divided by 4 in CSS\t\t*/")
        log_lines.append("#define HSPP_CSS_ROUNDS\t\t5\t\t/* Maximum number of rounds for CSS phase\t\t\t\t\t*/")
        log_lines.append("#define HSPP_DEACTIVE\t\t0")
        log_lines.append("#define HSPP_IN_SS\t\t1\t\t/* SS phase is active\t\t\t\t\t\t\t\t*/")
        log_lines.append("#define HSPP_IN_CSS\t\t2\t\t/* CSS phase is active\t\t\t\t\t\t\t\t*/")
        log_lines.append("#define HSPP_RTT_THRESH(x)\tclamp(x, HSPP_MIN_RTT_THRESH, HSPP_MAX_RTT_THRESH)")
        log_lines.append("// HYSTARTPP_defs_end. ---  (from RFC 9406)")
        log_lines.append("// RttThresh = max(MIN_RTT_THRESH, min(lastRoundMinRTT / MIN_RTT_DIVISOR, MAX_RTT_THRESH))")
        log_lines.append("// if (currentRoundMinRTT >= (lastRoundMinRTT + RttThresh))")
        log_lines.append("//   cssBaselineMinRtt = currentRoundMinRTT")
        log_lines.append("//   exit slow start and enter CSS\n")

        for idx, prev, new in transitions:
            ts = t_s[idx]
            rc = round_ctr[idx]
            lmin = last_min[idx]
            cmin = curr_min[idx]
            ctr = rtt_ctr[idx]
            base = css_base[idx]
            ent = entered_css_round[idx]

            raw_line = line_no[idx] if idx < len(line_no) else None
            line_label = raw_line if raw_line is not None else idx

            header = (f"line={line_label}, time={ts:.6f}s, round={rc}, "
                      f"flag {prev}->{new}")

            if (prev in (HSPP_DEACTIVE,) and new == HSPP_IN_SS):  # SS enter: 0 to 1
                events_ss.append(idx)
                log_lines.append("[SS ENTRY] " + header)
                log_lines.append(
                    f"  rtt_ctr={ctr}, last_min={lmin}, curr_min={cmin}, "
                    f"cssBaselineMinRtt={base}, entered_css_at_round={ent}\n"
                )

            elif (prev == HSPP_IN_CSS and new == HSPP_IN_SS):  # CSS abort: 2 to 1 (resume slow start)
                events_ss.append(idx)

                log_lines.append("[CSS ABORT->SS] " + header)

                j = max(idx - 1, 0) # Use previous baseline and current RTT at transition line
                prev_base = css_base[j]
                curr_now = curr_min[idx]

                cond = (
                    curr_now is not None and prev_base is not None
                    and curr_now != INF_U32 and prev_base != INF_U32
                    and curr_now < prev_base
                )

                prev_line_label = (line_no[j] if j < len(line_no) and line_no[j] is not None else j)

                log_lines.append(
                    f"  previous_line={prev_line_label}, prev_round={round_ctr[j]}, "
                    f"prev_cssBaselineMinRtt={prev_base}, "
                    f"currentRoundMinRTT_at_transition={curr_now}"
                )
                log_lines.append(
                    "  condition (currentRoundMinRTT < cssBaselineMinRtt) "
                    f"= {cond}"
                )
                log_lines.append(
                    f"  new cssBaselineMinRtt={base}\n"
                )

            elif (prev == HSPP_IN_SS and new == HSPP_IN_CSS):  # CSS enter: 1 to 2
                events_css.append(idx)
                log_lines.append("[CSS ENTRY] " + header)
                log_lines.append(
                    f"  rtt_ctr={ctr}, last_round_minrtt={lmin}, "
                    f"current_round_minrtt={cmin}, "
                    f"cssBaselineMinRtt={base}, "
                    f"entered_css_at_round={ent}"
                )

                # RTTThresh validation block
                rtt_thresh = compute_rtt_thresh_us(lmin)
                if (rtt_thresh is None or cmin is None or cmin == INF_U32
                        or lmin is None or lmin == INF_U32):
                    log_lines.append("  [RTTTHRESH CHECK] insufficient data to compute threshold\n")
                else:
                    boundary = lmin + rtt_thresh
                    ok = (cmin >= boundary)
                    log_lines.append("  [RTTTHRESH CHECK]")
                    log_lines.append(f"    last_round_minrtt={lmin} us")
                    log_lines.append(f"    current_round_minrtt={cmin} us")
                    log_lines.append(f"    computed_rtt_thresh={rtt_thresh} us")
                    log_lines.append(f"    last_plus_thresh={boundary} us")
                    log_lines.append(f"    condition current >= last+thresh : {'PASS' if ok else 'FAIL'}\n")

            elif (prev in (HSPP_IN_SS, HSPP_IN_CSS) and new == HSPP_DEACTIVE):  # HyStart++ off
                events_off.append(idx)
                log_lines.append("[HSPP OFF] " + header)
                log_lines.append(
                    f"  rtt_ctr={ctr}, last_min={lmin}, curr_min={cmin}, "
                    f"cssBaselineMinRtt={base}, entered_css_at_round={ent}\n"
                )

        
        dur = compute_state_durations(t_s, flags) # State summary logs
        total = (t_s[-1] - t_s[0]) if len(t_s) >= 2 else 0.0
        log_lines.append("\n[STATE DURATION SUMMARY]")
        log_lines.append(f"  total_time={total:.6f}s")
        log_lines.append(f"  time_in_SS={dur[HSPP_IN_SS]:.6f}s")
        log_lines.append(f"  time_in_CSS={dur[HSPP_IN_CSS]:.6f}s")
        log_lines.append(f"  time_in_DEACTIVE={dur[HSPP_DEACTIVE]:.6f}s\n")

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

