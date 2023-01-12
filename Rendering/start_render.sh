#!/bin/bash

folder=$1

for file in $folder/*.job; do
    dos2unix $file
done

while [[ $(qstat | grep -c $folder) -ne 0 ]]; do
  for file in $folder/*.job; do
    jobname=$(basename $file .job)
    if [[ $(qstat | grep $jobname) ]]; then
      echo "Job $jobname already submitted."
    else
      echo "Submitting job $jobname."
      qsub $file 
        if [ $? -eq 0 ]; then
            echo "job $file queued"
        else
            echo " queue limit reached finish for now."
        fi 
    fi
  done
  sleep 180 
done

echo "All jobs in $folder have been submitted"