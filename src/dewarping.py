#usr/bin/env python3
import os
import subprocess
import shutil
import threading
import argparse
import time

def dewarp_single_image(img_path, additional_args):
    print(f"Processing {img_path}...")
    
    # Default arguments for 'page-dewarp'
    default_args = ['-nb', '1']
    
    # Run the 'page-dewarp' utility
    subprocess.run(['page-dewarp', img_path] + default_args + additional_args)

def move_dewarped_images(dest_folder):
    current_dir = os.getcwd()
    
    # Loop through each file in the current directory
    for img_name in os.listdir(current_dir):
        if img_name.endswith(('_thresh.jpg', '_thresh.jpeg', '_thresh.png')):
            dewarped_img_path = os.path.join(current_dir, img_name)
            shutil.move(dewarped_img_path, os.path.join(dest_folder, img_name))

# Function to dewarp all images in a source folder and store them in a destination folder
def dewarp_images(src_folder, dest_folder, additional_args):
    if not os.path.exists(src_folder):
        print("Source folder does not exist.")
        return

    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    threads = []

    for img_name in os.listdir(src_folder):
        if img_name.endswith(('.jpg', '.jpeg', '.png')):
            img_path = os.path.join(src_folder, img_name)
            thread = threading.Thread(target=dewarp_single_image, args=(img_path, additional_args))
            threads.append(thread)
            thread.start()

    for thread in threads:
        thread.join()

    # Move the dewarped images after all threads have finished
    move_dewarped_images(dest_folder)

    print("All images have been processed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Dewarp images in a folder.')
    parser.add_argument('src_folder', help='Source folder containing images to be dewarped.')
    parser.add_argument('dest_folder', help='Destination folder to store dewarped images.')
    parser.add_argument('--additional_args', nargs='*', default=[], help='Additional command-line arguments for page-dewarp.')
    args = parser.parse_args()
    dewarp_images(args.src_folder, args.dest_folder, args.additional_args)
