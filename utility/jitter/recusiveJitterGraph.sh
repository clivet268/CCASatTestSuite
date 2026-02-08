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
    local file="$1"

    echo "Processing: $file"
    $PYTHON_EXE "$PYTHON_SCRIPT" "$file" 
}

########################################
# Walk through inputs
########################################

for path in "$@"; do

    if [ -f "$path" ]; then
        process_file "$path"

    elif [ -d "$path" ]; then
        # Recursively find files
        while IFS= read -r -d '' file; do
            process_file "$file"
        done < <(find "$path" -type f -print0)

    else
        echo "Warning: $path is not a valid file or directory"
    fi

done
