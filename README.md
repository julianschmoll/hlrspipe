# HLRS Rendering
## Setup
The scripts located in the Export folder should be added to mayas python environment, the Rendering scripts have to be located where batch jobs can be submitted to the high performance computing center. 
## Export
From the maya gui, all of the files are exported to a local directory, before they can be synced to the computing center. The scene name must be the same name like the folder structure in the sequences folder at HLRS. Also the output directory name is specified here.
After the export is completed, the seq files can be transferred to the high-performance data center with ```rsync -a -P {ass_file_directory} {sequence_folder}```. 
The job files are synchronized to the job folder with command ```rsync -a -P {ass_file_directory} {job_folder}```.
## Rendering
To start the rendering the script ```sh start_render.sh {job_folder}``` is used. The folder in which all job files are located must be specified here.
## Getting rendered files
to get the rendered .exr in the out folder, run the rsync command from the out folder ```rsync -a -P {out_folder} {local_out_folder}```