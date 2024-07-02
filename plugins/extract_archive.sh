#!/bin/bash

# Check if the first argument is the archive file path
if [ -z "$1" ]; then
  echo "Error: Archive file path not provided."
  exit 1
fi

archive_file="$1"

# Check if the second argument is the destination folder path (optional)
if [ -n "$2" ]; then
  dest_folder="$2"
else
  dest_folder=$(dirname "$archive_file")  # Default to the same directory as the archive
fi

# Extract ZIP archive
if [ "${archive_file##*.}" == "zip" ]; then
  unzip -d "$dest_folder" "$archive_file"
# Extract RAR archive 
elif [ "${archive_file##*.}" == "rar" ]; then
  unrar x -o- "$archive_file" "$dest_folder"  
# Handle other archive formats if needed
else
  echo "Unsupported archive format."
  exit 1
fi

# Output message (optional)
echo "Archive extracted successfully to $dest_folder"
