#!/bin/bash

# Check if the correct number of arguments are passed
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <source_directory> <target_directory>"
    exit 1
fi

SOURCE_DIR="$1"
TARGET_DIR="$2"

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Source directory $SOURCE_DIR does not exist."
    exit 1
fi

# Create target directory if it doesn't exist
if [ ! -d "$TARGET_DIR" ]; then
    mkdir -p "$TARGET_DIR"
fi

# Iterate over each image in the source directory and dewarp it
for img in "$SOURCE_DIR"/*.{jpg,jpeg,png}; do
    # Check if the image file exists (this will prevent issues in case there are no matches)
    if [ -f "$img" ]; then
        echo "Processing $img..."
        # Run page-dewarp on the image without changing directories
        page-dewarp "$img" -nb 1 -x 25 -y 50
        # Get the filename from the full path
        filename=$(basename "$img")
        # Move the processed image to the target directory
        mv "$img" "$TARGET_DIR/$filename"
    fi
done

echo "Dewarping complete. Processed images are in $TARGET_DIR."
