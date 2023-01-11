#!/bin/bash

## Ausführen des Skripts: sh job_generator <Sequenzname> 
## <Sequenzname> muss ein Ordner im Sequenzenordner auf dem Workspace sein.

if [ $# -ne 1 ]; then
  echo "ERROR $0: need shot Directory"
  echo "         USAGE:   $0   shot"
  exit 1
fi

=$1

ARNOLD_WORK_SPACE=/lustre/hpe/ws10/ws10.1/ws/zmcbeber-workspace1/zmcbeber-workspace1/sequenzen
ARNOLD_ROOT=/zhome/academic/HLRS/zmc/zmcbeber/Arnold_SDK-7.1.3.1_Linux

# Location of ass files that should be rendered
SEQ_DIR_NAME=${ARNOLD_WORK_SPACE}/${SEQUENZ_NAME}

# Location of .job files
JOB_DIR=${ARNOLD_ROOT}/Job_dir/${SEQUENZ_NAME}

if [ ! -d ${SEQ_DIR_NAME} ]; then
   echo " Error $0 has been started with shot name ${SEQUENZ_NAME}, but"
   echo " directory ${SEQ_DIR_NAME} is not available"
   exit 1
fi

cd ${JOB_DIR}
if [ $? -ne 0 ]; then
    echo "ERROR: Can't change into Job directory ${JOB_DIR}"
    exit
fi

STATUS=unknown
for x in `ls -1 ${INPUT_DIR_NAME}`; do    
    File=`basename $x.ass`
    echo $File

    if [ -f ${STATUS_DIR_NAME}/${File}.status ]; then
        STATUS=`cat ${STATUS_DIR_NAME}/${File}.status`  
    else
        echo "new" > ${STATUS_DIR_NAME}/${File}.status
        STATUS=new
    fi

    if [ "${STATUS}" = "new" ]; then
        sed  -e "s#__ARNOLD_WORK_SPACE__#${ARNOLD_WORK_SPACE}#g"   \
            -e "s#__SEQUENZ_NAME__#${SEQUENZ_NAME}#g"        \
            -e "s#__INPUT_DIR_NAME__#${INPUT_DIR_NAME}#g"        \
            -e "s#__OUTPUT_DIR_NAME__#${OUTPUT_DIR_NAME}#g"      \
            -e "s#__LOG_DIR_NAME__#${LOG_DIR_NAME}#g"            \
            -e "s#__STATUS_DIR_NAME__#${STATUS_DIR_NAME}#g"      \
            -e "s#__STATUS_FILE_NAME__#${File}.status#g"            \
            -e "s#__ARNOLD_INPUT_FILE__#${x}#g"                  \
            -e "s#__ARNOLD_LOG_FILE__#${File}.log#g"             \
            -e "s#__ARNOLD_OUTPUT_FILE__#${File}.exr#g"          \
            -e "s#__ARNOLD_JOB_NAME__#${File}.Job#g"                 \
        echo "job_generated" > ${STATUS_DIR_NAME}/${File}.status
        STATUS=job_generated
    fi

    if [ "${STATUS}" = "job_generated" ]; then
        qsub ${File}.Job
        if [ $? -eq 0 ]; then
                echo "job_queued" > ${STATUS_DIR_NAME}/${File}.status
            else
                echo " queue limit reached finish for now."
                exit 0 
        fi
    fi

    done

done

exit 0