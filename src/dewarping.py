#!/usr/bin/env python3
import os
import subprocess
import shutil
from concurrent.futures import ThreadPoolExecutor
import argparse
from .utils.logger_config import setup_logger
import time

logger = setup_logger()

class ImageDewarper:
    def __init__(self, src_folder=None, dest_folder=None, additional_args=None):
        self.src_folder = src_folder
        self.dest_folder = dest_folder
        self.additional_args = additional_args or []

    def dewarp_single_image(self, img_path, additional_args=None):
        if additional_args is None:
            additional_args = self.additional_args
        print(f"Processing {img_path}...")
        default_args = ['-nb', '1']
        subprocess.run(['page-dewarp', img_path] + default_args + additional_args)

    def move_dewarped_images(self):
        current_dir = os.getcwd()
        for img_name in os.listdir(current_dir):
            if img_name.endswith(('_thresh.jpg', '_thresh.jpeg', '_thresh.png')):
                dewarped_img_path = os.path.join(current_dir, img_name)
                shutil.move(dewarped_img_path, os.path.join(self.dest_folder, img_name))

    def dewarp_images(self):
        if not os.path.exists(self.src_folder):
            print("Source folder does not exist.")
            return

        if not os.path.exists(self.dest_folder):
            os.makedirs(self.dest_folder)

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.dewarp_single_image, os.path.join(self.src_folder, img_name)) 
                       for img_name in os.listdir(self.src_folder) 
                       if img_name.endswith(('.jpg', '.jpeg', '.png'))]

        for future in futures:
            future.result()  # to raise any exception that occurred during processing

        self.move_dewarped_images()
        print("All images have been processed.")

def main(args):
    dewarper = ImageDewarper(args.input_path, args.output_dir, args.additional_args)

    logger.info("Dewarping images...")
    start_time = time.time()
    if os.path.isdir(args.input_path):
        dewarper.dewarp_images()
    elif os.path.isfile(args.input_path):
        dewarper.dewarp_single_image(args.input_path)
        dewarper.move_dewarped_images()
    else:
        logger.error(f"Invalid input path: {args.input_path}")
    logger.info(f"Dewarping complete in {time.time() - start_time}.")

def parser_add_arguments(parser):
    parser.add_argument('input_path', help='Path of the image or folder to process.')
    parser.add_argument('output_dir', help='Destination folder to store processed images.')
    parser.add_argument('--additional_args', nargs='*', default=[], help='Additional command-line arguments for page-dewarp.')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Dewarp images in a folder.')
    parser_add_arguments(parser)
    args = parser.parse_args()
    main(args)