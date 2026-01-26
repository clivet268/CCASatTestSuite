#!/usr/bin/env python3
import os
import sys
import matplotlib.pyplot as plt

# --- Parsing Logic ---------------------------------------------------------

def parse_file(path):
    """Parse a log file and return a list of dict entries for each 'Line N:' block."""
    entries = []
    current = {}
    in_block = False

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()  # trim newline

            if line.startswith("Line "):
                if in_block and current:
                    entries.append(current)
                current = {}
                in_block = True
                continue

            if not in_block:
                continue

            if ":" in line:
                key, val = line.split(":", 1)
                key = key.strip()
                val = val.strip()
                try:
                    val = int(val)
                except ValueError:
                    pass
                current[key] = val

        if in_block and current:
            entries.append(current)

    return entries

# --- Plotting Logic --------------------------------------------------------

def plot_graph(entries, outpath, title_prefix=""):
    times = [e.get("now_us", None) for e in entries]
    cwnd = [e.get("snd_cwnd", None) for e in entries]
    rtt = [e.get("hspp_current_round_minrtt", None) for e in entries]
    flags = [e.get("hspp_flag", 0) for e in entries]

    # Two stacked subplots in one image
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10, 8))

    # --- Color by flag (1 = slow start, 2 = css, else red) ---
    colors = []
    for f in flags:
        if f == 1:
            colors.append("blue")
        elif f == 2:
            colors.append("orange")
        else:
            colors.append("red")

    # CWND subplot
    ax1.scatter(times, cwnd, s=10, c=colors)
    ax1.set_ylabel("cwnd")
    ax1.set_title(f"{title_prefix} cwnd vs time")

    # RTT subplot
    ax2.scatter(times, rtt, s=10, c=colors)
    ax2.set_xlabel("time (now_us)")
    ax2.set_ylabel("rtt")
    ax2.set_title(f"{title_prefix} rtt vs time")

    fig.tight_layout()
    plt.savefig(outpath + "_combined.png")
    plt.close()

# --- Directory / File Handling --------------------------------------------
# given a directory, recursively graphcs all logs, if given a list of logs, only does those

def process_file(input_file, output_root):
    rel = os.path.relpath(input_file)
    rel_no_ext = os.path.splitext(rel)[0]

    if os.path.isdir(input_file):
        return

    outdir = os.path.join(output_root, os.path.dirname(rel_no_ext))
    os.makedirs(outdir, exist_ok=True)

    outpath = os.path.join(outdir, os.path.basename(rel_no_ext))

    entries = parse_file(input_file)
    if entries:
        plot_graph(entries, outpath, rel)


def process_directory(root, output_root):
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if f.lower().endswith(".txt"):
                full = os.path.join(dirpath, f)
                process_file(full, output_root)

# --- Main ------------------------------------------------------------------

def main():
    if len(sys.argv) < 3:
        print("Usage: script.py <output_dir> <input_dir_or_file> [input2 ...]")
        sys.exit(1)

    output_root = sys.argv[1]
    os.makedirs(output_root, exist_ok=True)

    inputs = sys.argv[2:]

    for inp in inputs:
        if os.path.isdir(inp):
            process_directory(inp, output_root)
        elif os.path.isfile(inp):
            process_file(inp, output_root)
        else:
            print(f"Warning: {inp} does not exist")

if __name__ == "__main__":
    main()
