#!/bin/bash

# Get the path to the texture folder from the first command line argument
texture_folder=$1
broken_files=0
broken_files_list=()

# Set the path to the maketx executable
txmake_path='/zhome/academic/HLRS/zmc/zmcbeber/Arnold_SDK-7.1.3.1_Linux/bin/maketx'

# Iterate through all files in the texture folder
for file in "$texture_folder"/*
do
  # Check if the file is a texture file
  if [[ $file == *.jpg || $file == *.jpeg || $file == *.png || $file == *.exr || $file == *.tiff || $file == *.tif ]]; then
    # Check if the texture is broken
    if oiiotool "$file" -info > /dev/null 2>&1; then
      echo "$file is not broken"
    else
      # If the texture is broken, convert it to a non-broken file in the same format as the original one
      echo "$file is broken, converting..."
      filename=$(basename -- "$file")
      extension="${filename##*.}"
      filename="${filename%.*}"
      $txmake_path -compression none -color_space none -mipmap -format $extension -oiio "$file" "$texture_folder/$filename.$extension"
      rm "$file"
      broken_files+=1
      broken_files_list+=("$file")
      echo "$file is broken and has been converted"
    fi
  fi
done
echo "Number of broken files: $broken_files"
echo "List of broken files: ${broken_files_list[@]}"
