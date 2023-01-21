#!/bin/bash

path_variable=$1
log_path="/lustre/hpe/ws10/ws10.1/ws/zmcbeber-workspace1/zmcbeber-workspace1/sequenzen/out/StuProPanda/$path_variable/logs"
job_path="/zhome/academic/HLRS/zmc/zmcbeber/Arnold_SDK-7.1.3.1_Linux/Job_dir"
failed_frames=$(grep -l "/lib64/libX11.so.6: cannot read file data: Input/output error" $log_path/*)

for frame in $failed_frames
do
    job_file=$(echo $frame | sed "s|$log_path/render_||" | sed 's/\.log$/.Job/')
    qsub "$job_path/$job_file"
done