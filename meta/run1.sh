#!/bin/bash

# Get the PID and TIME columns from the ps aux output
# and filter out the header line
ps_aux_output=$(ps aux --sort=start_time | awk 'NR>1{print $2,$10}')

# Iterate over each line of ps aux output
while read -r pid time; do
    # Extract minutes and seconds from the TIME column
    minutes=$(cut -d':' -f1 <<< "$time")
    seconds=$(cut -d':' -f2 <<< "$time")

    # Calculate total seconds
    total_seconds=$((minutes * 60 + seconds))

    # Check if the process has exceeded the time limit (50 seconds)
    if [ "$total_seconds" -gt 50 ]; then
        # Kill the process
        if kill "$pid" >/dev/null 2>&1; then
            echo "$(date): Killed process with PID $pid (TIME: $time)"
        else
            echo "$(date): Failed to kill process with PID $pid (TIME: $time)"
        fi
    fi
done <<< "$ps_aux_output"
