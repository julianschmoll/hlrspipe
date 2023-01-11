#!/bin/bash

if [ $# -ne 1 ]; then
  echo "ERROR $0: need .ass Directory"
  exit 1
fi

SEQUENZ_NAME=$1

ARNOLD_WORK_SPACE=/lustre/hpe/ws10/ws10.1/ws/zmcbeber-workspace1/zmcbeber-workspace1/sequenzen
ARNOLD_ROOT=/zhome/academic/HLRS/zmc/zmcbeber/Arnold_SDK-7.1.3.1_Linux

# Location of ass files that should be rendered
SEQ_DIR_NAME=${ARNOLD_WORK_SPACE}/${SEQUENZ_NAME}

# Location of .job files
JOB_DIR=${ARNOLD_ROOT}/Job_dir/${SEQUENZ_NAME}

if [ ! -d ${SEQ_DIR_NAME} ]; then
   echo " Error directory ${SEQ_DIR_NAME} is not available"
   exit 1
fi

cd ${JOB_DIR}
if [ $? -ne 0 ]; then
    echo "ERROR: Can't change into Job directory ${JOB_DIR}"
    exit
fi

for x in `ls -1 ${JOB_DIR}`; do    
    qsub $x
    if [ $? -eq 0 ]; then
            echo "job ${x} queued"
        else
            echo " queue limit reached finish for now."
            exit 0
        fi 
    fi
done

exit 0