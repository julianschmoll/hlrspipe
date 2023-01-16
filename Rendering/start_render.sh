#!/bin/bash

folder=$1

status_file="$folder/status.txt"
touch $status_file

while true; do
    all_submitted=true
    for file in $folder/*.Job; do
        jobname=$(basename $file .Job)
        if grep -q $jobname $status_file; then
            echo "Job $jobname already submitted."
        else
            all_submitted=false
            dos2unix $file
            echo "Submitting job $jobname."
            qsub $file
            if [ $? -eq 0 ]; then
                echo "job $file queued"
                echo $jobname >> $status_file
            else
                echo " queue limit reached finish for now."
                break
            fi 
        fi
    done
    if [ "$all_submitted" = true ]; then
        echo "All jobs in $folder have been submitted"
        break
    else
        sleep 180 
    fi
done
