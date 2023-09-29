#!/usr/bin/env python3
import os
import subprocess
import shutil
import threading
import argparse

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

        threads = []

        for img_name in os.listdir(self.src_folder):
            if img_name.endswith(('.jpg', '.jpeg', '.png')):
                img_path = os.path.join(self.src_folder, img_name)
                thread = threading.Thread(target=self.dewarp_single_image, args=(img_path,))
                threads.append(thread)
                thread.start()

        for thread in threads:
            thread.join()

        self.move_dewarped_images()
        print("All images have been processed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Dewarp images in a folder.')
    parser.add_argument('src_folder', help='Source folder containing images to be dewarped.')
    parser.add_argument('dest_folder', help='Destination folder to store dewarped images.')
    parser.add_argument('--additional_args', nargs='*', default=[], help='Additional command-line arguments for page-dewarp.')
    args = parser.parse_args()

    dewarper = ImageDewarper(args.src_folder, args.dest_folder, args.additional_args)
    dewarper.dewarp_images()
