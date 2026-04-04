#!/usr/bin/env bash
# created by chatgpt
set -euo pipefail

########################################
# Config — change this to your script
########################################
PYTHON_SCRIPT="jitter.py"
PYTHON_EXE="python3"

########################################
# Parse arguments
########################################

USE_M=false

# Parse optional -M flag
while getopts ":M" opt; do
    case "$opt" in
        M)
            USE_M=true
            ;;
        *)
            echo "Usage: $0 [-M] <jitterAmount> <file_or_dir> [more files/dirs...]"
            exit 1
            ;;
    esac
done

# Shift past options
shift $((OPTIND - 1))

# Require jitter amount
if [ "$#" -lt 2 ]; then
    echo "Usage: $0 [-M] <jitterAmount> <file_or_dir> [more files/dirs...]"
    exit 1
fi

JITTER="$1"
shift

########################################
# Function to process a single file
########################################
process_file() {
    local file="$1"

    echo "Processing: $file"

    if [ "$USE_M" = true ]; then
        $PYTHON_EXE "$PYTHON_SCRIPT" -M "$file" "$JITTER"
    else
        $PYTHON_EXE "$PYTHON_SCRIPT" "$file" "$JITTER"
    fi
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
