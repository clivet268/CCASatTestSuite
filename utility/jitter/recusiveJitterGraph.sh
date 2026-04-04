#!/usr/bin/env bash
# created by chatgpt - and slightly modified
set -euo pipefail

########################################
# Config — change this to your script
########################################
PYTHON_SCRIPT="graphJitter.py"
PYTHON_EXE="python3"

########################################
# Function to process a single file
########################################
process_file() {
    local file2="$1"
    local file="$2"
    local maxTime="$3"

    echo "Processing: $file"
    $PYTHON_EXE "$PYTHON_SCRIPT" "$file2" "$file" "$maxTime" 
}

########################################
# Walk through inputs
########################################
graphXLimit=$1
srcfile=$2
shift
for path in "$@"; do

    if [ -f "$path" ]; then
        process_file "$srcfile" "$path" "$graphXLimit"

    elif [ -d "$path" ]; then
        # Recursively find files
        while IFS= read -r -d '' file; do
            process_file "$srcfile" "$file" "$graphXLimit"
        done < <(find "$path" -type f -print0)

    else
        echo "Warning: $path is not a valid file or directory"
    fi

done
