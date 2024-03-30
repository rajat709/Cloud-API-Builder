#!/bin/bash

# Customizable parameters
TIME_LIMIT=50  # Time limit in seconds
LOG_FILE="/var/log/process_killer.log"

# Function for logging messages
log() {
    timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo "$timestamp: $1" >> "$LOG_FILE"
}

# Function for safe killing using escalating signals
safe_kill() {
    pid=$1
    time=$2

    # First attempt a graceful termination (SIGTERM)
    kill "$pid" && log "Sent SIGTERM to process $pid (TIME: $time)" && return 0 

    # If that fails, try a more forceful termination (SIGKILL)
    sleep 5  # Allow some time for cleanup
    kill -9 "$pid" && log "Sent SIGKILL to process $pid (TIME: $time)" && return 0

    # If all else fails, log an error 
    log "Failed to kill process $pid (TIME: $time)" 
    return 1
}

# Get process info with error handling
ps_aux_output=$(ps aux | awk '{print $2,$10}' | tail -n +2) || {
    log "Error getting process information"
    exit 1
}

# Process the output
while read -r line; do
    pid=$(echo "$line" | awk '{print $1}')
    time=$(echo "$line" | awk '{print $2}')

    # Extract run time components
    minutes=$(echo "$time" | cut -d':' -f1)
    seconds=$(echo "$time" | cut -d':' -f2)

    total_seconds=$((minutes * 60 + seconds))

    if [ "$total_seconds" -gt "$TIME_LIMIT" ]; then
        safe_kill "$pid" "$time" 
    fi
done <<< "$ps_aux_output"
