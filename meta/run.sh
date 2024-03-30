#!/bin/bash

# Get the list of running processes
process_list=$(ps)

# Loop through each process
while read -r line; do
    pid=$(echo "$line" | awk '{print $1}')
    elapsed_time=$(echo "$line" | awk '{print $3}')

    # Skip the header line of ps output
    if [[ "$pid" == "PID" ]]; then
        continue
    fi

    # Check if the process has exceeded the time limit (50 seconds)
    if [ "$elapsed_time" -gt 50 ]; then
        echo "Process with PID $pid has exceeded the time limit. Killing..."
        kill -9 "$pid"
    fi
done <<< "$process_list"
