import pymel.core as pc
import json
import os
import shutil
import time

from concurrent import futures
from pathlib import Path


def copy_worker(src_and_target: tuple):
    source, target = src_and_target
    print(f"{source} - Copying")
    try:
        shutil.copy2(source, target)
    except (FileNotFoundError, PermissionError) as e:
        print(f"{source} - ERROR: {e}")


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
    
    print("starting copy threads ...")
    with futures.ThreadPoolExecutor() as exec:
        jobs = [
            exec.submit(copy_worker, (Path(src), dest / Path(src).name))
            for src in set(filepaths)
        ]
        for job in futures.as_completed(jobs):
            # Nothing to do here really, we just don't want to use
            # futures.wait() since that could freeze Maya.
            time.sleep(1)
            pass

    return folders


def write_pathmap(folders, resources, filepath):
    """Writes pathmap which can be read by arnold batch renderer
    
    Args:
        folders: set of folders where ressources are in at the moment
        resources: name of relative resource folder in pathmap
        filepath: path where pathmap is written to
        
    Returns:
        pathmap
    
    """
    ocio_config = pc.colorManagementPrefs(q=True, configFilePath=True)
    
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
        
      
def write_job_file(filepath, name, SEQUENZ_NAME, out_dir_name):
    """Writes a job file which can be used to start the render at HLRS
    
    Args:
        filepath: path where pathmap is written to
        name: name of the job file
        sequenz_name: name of the sequence 
        out_dir_name: name of output directory at hlrs
        
    Returns:
        job file
    
    """
    
    folder = Path(name).parent.absolute()
    ass_name = Path(name).name
    ass_name = f"{ass_name}.ass"
    
    script_dir = os.path.dirname(__file__)
    os.chdir(script_dir)
    
    # writes job file from template
    with open('job_template.txt', 'r') as f:
        template = f.read()
    
    result = template.format(ASS_FILE_NAME = ass_name, 
                             SCENE_NAME = SEQUENZ_NAME,
                             OUT_DIR_NAME = out_dir_name)
    
    subfolder = "job"
    subfolder_path = os.path.join(folder, subfolder)
    os.makedirs(subfolder_path, exist_ok=True)
    
    outFileName=f"{subfolder_path}/{ass_name}.Job"
    outFile=open(outFileName, "w")
    outFile.write(result)
    outFile.close()