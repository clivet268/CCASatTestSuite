#!/usr/bin/bash
# Calls the inner jitter script multiple times,
# with jitter increasing by a fixed step each iteration.
set -euo pipefail

INNER_SCRIPT="./recusiveJitter.sh"

########################################
# Usage
########################################
usage() {
    echo "Usage: $0 [-M] -n <count> -s <start> -i <increment> <file_or_dir> [more files/dirs...]"
    echo ""
    echo "  -M            Pass -M flag through to the inner script"
    echo "  -n <count>    Number of times to call the inner script"
    echo "  -s <start>    Starting jitter amount"
    echo "  -i <increment> Amount to increase jitter by each call"
    echo ""
    echo "Example: $0 -n 5 -s 10 -i 5 ./myfile.txt"
    echo "  -> calls inner script with jitter 10, 15, 20, 25, 30"
    exit 1
}

########################################
# Parse arguments
########################################
USE_M=false
COUNT=""
START=""
INCREMENT=""

while getopts ":Mn:s:i:" opt; do
    case "$opt" in
        M) USE_M=true ;;
        n) COUNT="$OPTARG" ;;
        s) START="$OPTARG" ;;
        i) INCREMENT="$OPTARG" ;;
        *) usage ;;
    esac
done

shift $((OPTIND - 1))

# Validate required flags
if [ -z "$COUNT" ] || [ -z "$START" ] || [ -z "$INCREMENT" ]; then
    echo "Error: -n, -s, and -i are all required."
    usage
fi

# Validate at least one file/dir target
if [ "$#" -lt 1 ]; then
    echo "Error: At least one file or directory must be provided."
    usage
fi

# Validate that COUNT, START, INCREMENT are numeric
for val_name in "COUNT:$COUNT" "START:$START" "INCREMENT:$INCREMENT"; do
    name="${val_name%%:*}"
    val="${val_name##*:}"
    if ! [[ "$val" =~ ^-?[0-9]+(\.[0-9]+)?$ ]]; then
        echo "Error: $name must be a number (got: '$val')"
        exit 1
    fi
done

########################################
# Run inner script N times
########################################

# Use awk for float arithmetic
jitter="$START"

for (( call=1; call<=COUNT; call++ )); do
    echo "========================================"
    echo "Call $call / $COUNT  —  jitter = $jitter"
    echo "========================================"

    if [ "$USE_M" = true ]; then
        "$INNER_SCRIPT" -M "$jitter" "$@"
    else
        "$INNER_SCRIPT" "$jitter" "$@"
    fi

    # Increment jitter (float-safe via awk)
    jitter=$(awk "BEGIN { printf \"%.6g\", $jitter + $INCREMENT }")
done

echo ""
echo "Done. Ran $COUNT calls starting at jitter=$START, incrementing by $INCREMENT."