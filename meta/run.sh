#!/bin/bash

# Get the PID and TIME columns from the ps aux output
# and filter out the header line
ps_aux_output=$(ps aux | awk '{print $2,$10}' | tail -n +2)

# Iterate over each line of ps aux output
while read -r line; do
    pid=$(echo "$line" | awk '{print $1}')
    time=$(echo "$line" | awk '{print $2}')

    # Extract minutes and seconds from the TIME column
    minutes=$(echo "$time" | cut -d':' -f1)
    seconds=$(echo "$time" | cut -d':' -f2)

    # Calculate total seconds
    total_seconds=$((minutes * 60 + seconds))

    # Check if the process has exceeded the time limit (50 seconds)
    if [ "$total_seconds" -gt 50 ]; then
        # Kill the process
        kill -9 "$pid"
        echo "Killed process with PID $pid (TIME: $time)"
    fi
done <<< "$ps_aux_output"
