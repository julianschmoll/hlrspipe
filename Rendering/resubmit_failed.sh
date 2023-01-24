#!/bin/bash

# Set the variable for the path
path_variable=$1

# Set the path to the log files
log_path="/lustre/hpe/ws10/ws10.1/ws/zmcbeber-workspace1/zmcbeber-workspace1/sequenzen/out/$path_variable"
echo "log_path: $log_path"

# Set the path to the job files
job_path="/lustre/hpe/ws10/ws10.1/ws/zmcbeber-workspace1/zmcbeber-workspace1/Arnold_SDK-7.1.3.1_Linux/Job_dir"
echo "job_path: $job_path"


while "$all_submitted" = false; do
    all_submitted=true
    # Search for log files that contain the error message
    failed_frames=$(grep -rl "/lib64/libX11.so.6: cannot read file data: Input/output error" $log_path)

    # Loop through the failed frames and resubmit the job
    for frame in $failed_frames
    do
        # Get the job file name from the log file path
        job_file=$(echo $frame | sed "s|$log_path/render_||" | sed 's/\.log$/.Job/')
        echo "job_file: $job_file"
        
        # Submit the job again
        all_submitted=false
        qsub "$job_path/$job_file"
    done
    sleep 180
done