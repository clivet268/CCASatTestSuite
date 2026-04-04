#! /usr/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <input_directory>"
    exit 1
fi

INPUT_ROOT="$1"
OUTPUT_ROOT="${2:-graph}"

if [ ! -d "$INPUT_ROOT" ]; then
    echo "Error: '$INPUT_ROOT' is not a valid directory"
    exit 1
fi

find "$INPUT_ROOT" -type d | while read -r input_dir; do
    # Compute the relative path from the input root, then mirror it under result/
    relative="${input_dir#$INPUT_ROOT}"
    relative="${relative#/}"  # strip any leading slash

    if [ -z "$relative" ]; then
        output_dir="$OUTPUT_ROOT"
    else
        output_dir="$OUTPUT_ROOT/$relative"
    fi

    echo "Processing: $input_dir -> $output_dir"
    python3 plot_hystartpp_dir.py  "$input_dir" "$output_dir"
done