import pymel.core as pc
import json
import os

from pathlib import Path
from shutil import copy


def collect_files(dest: str, image_suffix_list : list = None) -> list:
    """Collects and copies referenced files to destination
    
    Args:
        dest: Destination folder
        
    Returns:
        List of source folders
    
    """
    if image_suffix_list is None:
        image_suffix_list = [".png", ".tif", ".tiff", ".exr", ".jpeg", ".jpg", ".bmp"]
    dest = Path(dest)
    
    files = pc.ls(type="file")
    abcs = pc.ls(type="AlembicNode")
    standins = pc.ls(type="aiStandIn")
    filepaths = []
    folders = set()
    
    for file in files:
        filepath = Path(file.fileTextureName.get())
        filepaths.append(filepath)
        folders.add(filepath.parent)
        tx_file = filepath.parent / (filepath.stem + ".tx")
        if filepath.suffix in image_suffix_list and tx_file.exists():
            filepaths.append(tx_file)
        
    for abc in abcs:
        filepath = Path(abc.abc_File.get())
        filepaths.append(filepath)
        folders.add(filepath.parent)
           
    for standin in standins:
        filepath = Path(standin.dso.get())
        filepaths.append(filepath)
        folders.add(filepath.parent)
        
    for filepath in set(filepaths):
        src = Path(filepath)
        try:
            copy(src, dest / src.name)
            print(f"Copying {src}")
        except FileNotFoundError:
            print(f"File {filepath} not found") 
        except PermissionError:
            print(f"No permission for {filepath}")

    return folders


def write_pathmap(folders, resources, filepath):
    ocio_config = pc.colorManagementPrefs(q=True, configFilePath=True)
    
    # we need two folders up
    ocio_parent_folder = os.path.dirname(ocio_config)
    ocio_parent_folder = os.path.dirname(ocio_parent_folder)
    
    ocio_pathmap_path = f"\u0022{ocio_parent_folder}\u0022:\u0022/ocio\u0022"
    print(ocio_pathmap_path)
    
    normalized_folders = []
    for folder in folders:
        if folder:
            normalized_folder = os.path.normpath(folder)
            normalized_folder = normalized_folder.replace("\\", "/")
            normalized_folders.append(normalized_folder)

    # Print the normalized folders
    print(normalized_folders)
    
    mapping = {
            str(normalized_folder): f"/{resources}"
            for normalized_folder in normalized_folders}
    
    mapping[f"{ocio_parent_folder}"] = "/ocio"
    
    
    pathmap = {
        "windows":mapping,
        "mac": mapping,
        "linux": mapping}

    with open(filepath/"pathmap.json", "w") as file:
        json.dump(pathmap, file, indent=4)
        
      
def write_sh_script(filepath, name):
    ass_name = Path(name).name
    ass_name = f"{ass_name}.ass"
    name = f"{name}ass.Job"
    
    SEQUENZ_NAME = "StuProPanda/testcube-v01"
    
    WORKSPACE_DIR_NAME="/lustre/hpe/ws10/ws10.1/ws/zmcbeber-workspace1/zmcbeber-workspace1/sequenzen"
    ASS_ROOT_DIR_NAME="/StuProPanda/sh0002/"
    ASS_FILE_NAME=ass_name
    ARNOLD_ROOT_PATH="/zhome/academic/HLRS/zmc/zmcbeber/Arnold_SDK-7.1.3.1_Linux"
    ACES_PATH="/lustre/hpe/ws10/ws10.1/ws/zmcbeber-workspace1/zmcbeber-workspace1/ocio/aces_1.2"
    
    # Define the shell script as a string
    script = f"""
    #!/bin/bash
    #PBS -A zmcbeber
    #PBS -N shot_-sh002_ren_Rendering_v0005__js435_.ma_panda_layer.1001.ass
    # PBS -l nodes=1:ppn=24
    # PBS -l walltime=00:02:00
    #PBS -l select=1:node_type=rome,walltime=0:20:00

    ## In den PBS-Header muss später die HdM-Queue eingetragen werden.
    ## Damit wird verhindert, dass Render-Jobs in die Testqueue
    ## des HLRS übergeben werden. Das betrifft alle Jobs, die weniger
    ## als 30 Minuten rendern. Insgesamt stehen dann schneller mehr Ressourcen zur Verfügung.

    WORKSPACE_DIR_NAME={WORKSPACE_DIR_NAME}
    ASS_ROOT_DIR_NAME={ASS_ROOT_DIR_NAME}
    ASS_FILE_NAME={ASS_FILE_NAME}
    ARNOLD_ROOT_PATH={ARNOLD_ROOT_PATH}
    ACES_PATH={ACES_PATH}

    "$ARNOLD_ROOT/bin/kick"

    set -x

    cd 


    if [ $? -ne 0 ]; then
        echo "Error: can't change into $WORKSPACE_DIR_NAME"
        echo " aborting..."
        exit 1
    fi

   SEQUENZ_NAME={SEQUENZ_NAME}
   INPUT_DIR_NAME=$WORKSPACE_DIR_NAME/$ASS_ROOT_DIR_NAME
   OUTPUT_DIR_NAME=$WORKSPACE_DIR_NAME/$ASS_ROOT_DIR_NAME/Export
   LOG_DIR_NAME=$WORKSPACE_DIR_NAME/$ASS_ROOT_DIR_NAME/Logs
   STATUS_DIR_NAME=$WORKSPACE_DIR_NAME/$ASS_ROOT_DIR_NAME/$ASS_FILE_NAME.status

   STATUS_FILE=$STATUS_DIR_NAME/$ASS_FILE_NAME.status

    STATUS_FILE=$STATUS_DIR_NAME/$ASS_FILE_NAME.status

    #root paths
    export ARNOLD_ROOT=$ARNOLD_ROOT_PATH
    export ASS_ROOT=$WORKSPACE_DIR_NAME/$ASS_ROOT_DIR_NAME

    # substitue and replace fullpaths in ass-file:
    export ARNOLD_PATHMAP="$WORKSPACE_DIR_NAME/$ASS_ROOT_DIR_NAME/pathmap.json"

    PATH=$PATH:$ARNOLD_ROOT/bin/:$ARNOLD_ROOT/bin
    export PATH

    #kick path
    export KICK="$ARNOLD_ROOT/bin/kick"

    #custom attributes (-dw for disable preview)
    export CUSTOM_ATTRIBUTES="-dw -dp -nokeypress -v 6"

    #ld library path
    export LD_LIBRARY_PATH="$ARNOLD_ROOT/bin"

    #pluging or shader path
    export SHADER="-l $ARNOLD_ROOT/shaders"

    #texture path
    export TEXTURES="-set options.texture_searchpath $WORKSPACE_DIR_NAME/$ASS_ROOT_DIR_NAME"

    #procedural path (path to ass files)
    export PROCEDURALS="-set options.procedural_searchpath $WORKSPACE_DIR_NAME/$ASS_ROOT_DIR_NAME"

    #Bernd....
    #ocio-path should also be on the arnold-distribution or....
    # export OCIOPATH="-set color_manager_ocio.config $ARNOLD_ROOT/ocio/configs/arnold/config.ocio"
    export OCIOPATH="-set color_manager_ocio.config $ACES_PATH/config.ocio"

    #arnold license
    export solidangle_LICENSE=""2080@ca-lic.hdm-stuttgart.de""
    export RLM_LICENSE="(not set)"
    export ADSKFLEX_LICENSE_FILE="@ca-lic.hdm-stuttgart.de"
    export LM_LICENSE_FILE="(not set)"

    ## 5053 ist standardmäßig als Port festgelegt für den RLM Service.
    ## Der Port kann in der License-File von Solidangle geändert werden.
    ## Nach einer Änderung muss der Lizenzserver neugestartet werden.
    ## Je nach Lizenzpaket müssen unterschiedliche Variablen gesetzt werden.

    #saving path
    export SAVING_PATH="$OUTPUT_DIR_NAME/$ASS_FILE_NAME.exr"


    if [ ! -f $INPUT_DIR_NAME ]; then
            echo " Error: File $INPUT_DIR_NAME does not exist. Abort..."
            exit 1
    fi

    if [ ! -f $STATUS_FILE ]; then
        echo " Error: Status file $STATUS_FILE is not available. This is a unknown situation Abort..."
        exit 1
    fi

    ## Status wird gecheckt und auf "running" gesetzt, um zu verhindern,
    ## dass Jobs mehrfach abgeschickt werden können.
    STATUS=`cat $STATUS_FILE`
    if [ "$STATUS" != "job_queued" ]; then
        echo " ERROR $0  job status is not job_queued at Job start. Aborting"
        # exit 1
    fi
    echo "running" > $STATUS_FILE


    if [ ! -d $OUTPUT_DIR_NAME ]; then
        mkdir -p $OUTPUT_DIR_NAME
        if [ $? -ne 0 ]; then
            echo " Error: can't create Directory $OUTPUT_DIR_NAME. Abort..."
            echo "ERROR   can't create directory for output" > $STATUS_FILE
            exit 1
        fi
    fi



    if [ ! -d $LOG_DIR_NAME ]; then
        mkdir -p $LOG_DIR_NAME
        if [ $? -ne 0 ]; then
            echo " Error: can't create Directory $LOG_DIR_NAME. Abort..."
            echo "ERROR   can't create directory for log" > $STATUS_FILE
            exit 1
        fi
    fi

    # if we want to render seperate files of pathes:
    # -set defaultArnoldDriver@driver_exr.RGBA.direct_diffuse.filename "C:/temp/direct_diffuse.exr"


    WORKSPACE_DIR_NAME="/lustre/hpe/ws10/ws10.1/ws/zmcbeber-workspace1/zmcbeber-workspace1/sequenzen"
    ASS_ROOT_DIR_NAME="/StuProPanda/sh0002/"
    ASS_FILE_NAME="shot_-sh002_ren_Rendering_v0005__js435_.ma_panda_layer.1001.ass"

    #start rendering
    $KICK -i $WORKSPACE_DIR_NAME/$ASS_ROOT_DIR_NAME/$ASS_FILE_NAME    \
    $CUSTOM_ATTRIBUTES $SHADER $TEXTURES $PROCEDURALS $OCIOPATH   \
    -set driver_exr.filename $SAVING_PATH    \
    -o $SAVING_PATH \
    -logfile  $LOG_DIR_NAME/shot_-sh002_ren_Rendering_v0005__js435_.ma_panda_layer.1001.ass.log

    #  now create, submit, ... next jobs
    job_generator.sh  $SEQUENZ_NAME

    exit
    """

    # Change the current working directory to the desired folder
    os.chdir(filepath)

    # Create a file to store the shell script
    with open(name, "w") as f:
        f.write(script)

    # Make the shell script executable by everyone
    os.chmod(name, 0o777)