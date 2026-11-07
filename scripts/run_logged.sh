#!/bin/sh
set -u

log=$1
label=$2
shift 2

printf '\n=== %s | %s ===\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$label" >> "$log" || exit 1
printf '[START] %s\n' "$label"

bash -o pipefail -c '
    log=$1
    shift
    "$@" 2>&1 | tee -a "$log" | while IFS= read -r line; do
        case "$line" in
            "[MOLECULE] "*) printf "[MOLECULE] %s\n" "${line#\[MOLECULE\] }" ;;
        esac
    done
' -- "$log" "$@"
status=$?

if [ "$status" -eq 0 ]; then
    printf '[OK] %s\n' "$label" >> "$log" || exit 1
    printf '[OK] %s (Log: %s)\n' "$label" "$log"
else
    printf '[ERROR] %s | Exitcode: %s\n' "$label" "$status" >> "$log"
    printf '[ERROR] %s (Exitcode %s; Log: %s)\n' "$label" "$status" "$log" >&2
    tail -n 15 "$log" >&2
fi

exit "$status"
