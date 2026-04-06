import argparse
import subprocess
import os
import csv
from pathlib import Path


def find_stream_with_most_packets(pcap_file): 
    MAX_ITER = 10
    MIN_NUM_PKTS = 5000

    print(f"Searching for tcp.stream with more than {MIN_NUM_PKTS} packets...") 
    for i in range(0, MAX_ITER + 1):
        try:
            result = subprocess.run([r"C:\Program Files\Wireshark\tshark.exe", "-r", str(pcap_file), "tcp.stream", "eq", str(i)], stdout=subprocess.PIPE, check=True, text=True) # Run tshark to filter by tcp.stream and count packets, this uses my wireshark path for windows.
            pkt_count = result.stdout.count('\n') 
            if pkt_count > MIN_NUM_PKTS:
                print(f"Found tcp.stream {i} with {pkt_count} packets.")
                return i
        except subprocess.CalledProcessError:
            pass

    print(f"Error: Could not find tcp.stream with more than {MIN_NUM_PKTS} packets!")
    return None 

def convert_pcap_to_csv(pcap_file, csv_output):
    stream_number = find_stream_with_most_packets(pcap_file) # Find the iperf stream to extract this stream to CSV.
    if stream_number is None:
        return

    column_names = [
        "Time", "Source", "Destination", "Protocol", "Length", "Sequence number", "Ack number", "Ack_raw",
        "TSval", "TSecr", "duplicate_ack", "retransmission", "SACK", "CE", "byte in flight", "Lost segment", "Window Update", "Window Full",
        "ack_RTT" ,"advertised_window"
    ] # These are the fields we extract from tshark.

    command = [
        r"C:\Program Files\Wireshark\tshark.exe",
        "-r", str(pcap_file), # Read from pcap file
        f"-Y", f"tcp.stream eq {stream_number}", # Filter to the selected tcp stream
        "-T", "fields", 
        "-e", "frame.time_relative", 
        "-e", "ip.src", # Source IP
        "-e", "ip.dst", # Destination IP
        "-e", "ip.proto", # Protocol
        "-e", "frame.len", # Total frame length
        "-e", "tcp.seq", # Sequence number
        "-e", "tcp.ack", # Ack number
        "-e", "tcp.ack_raw", # Ack_raw
        "-e", "tcp.options.timestamp.tsval", # TSval
        "-e", "tcp.options.timestamp.tsecr", # TSecr
        "-e", "tcp.analysis.duplicate_ack_num", # duplicate_ack

        "-e", "tcp.analysis.retransmission", # retransmission
        "-e", "tcp.options.sack.count", # SACK
        "-e", "ip.dsfield.ecn", # CE (Congestion Experienced)
        "-e", "tcp.analysis.bytes_in_flight", # byte in flight
        "-e", "tcp.analysis.lost_segment", # Lost segment
        "-e", "tcp.analysis.window_update", # Window Update
        "-e", "tcp.analysis.window_full", # Window Full
        "-e", "tcp.analysis.ack_rtt", # ack_RTT
        "-e", "tcp.window_size", # advertised_window
        "-E", "separator=,", 
        "-E", "occurrence=f" # first occurrence of each field per packet
    ]

    try:
        with open(csv_output, "w") as output_file:
            output_file.write(','.join(column_names) + '\n')
            result = subprocess.run(command, stdout=subprocess.PIPE, check=True, text=True)
            output_file.write(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error converting '{pcap_file}':", e)


def main():
    ap = argparse.ArgumentParser(
        description="Convert *_45s.pcap files into per-run CSVs for mlcneta/b/c/d. The CSVs will contain packet-level data for the tcp stream with the most packets."
    )

    ap.add_argument("root", help="Path to folder containing mlcneta/mlcnetb/mlcnetc/mlcnetd")
    ap.add_argument("--testdir", required=True, help="Test directory name under each server (like viasatbig4_45_striped_4x160_test56)")
    ap.add_argument("--outdir", default="csv_outputs", help="Directory to save the output CSV files")
    args = ap.parse_args()

    servers = ["mlcneta", "mlcnetb", "mlcnetc", "mlcnetd"]
    for server in servers:
        server_path = Path(args.root) / server / args.testdir
        if not server_path.is_dir():
            print(f"Warning: Server directory not found for {server} at {server_path}. Skipping.")
            continue

        # Find the pcap files recursively from path
        pcap_files = list(server_path.rglob('*.pcap'))
        for pcap_file in pcap_files:
            output_dir = Path(args.outdir)
            output_dir.mkdir(parents=True, exist_ok=True)
            csv_output = output_dir / f"{server}_{pcap_file.stem}.csv"

            print(f"Processing {pcap_file}...")
            convert_pcap_to_csv(pcap_file, csv_output)

if __name__ == "__main__":
    main()
