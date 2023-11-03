#!/usr/bin/env python3
import argparse
import cv2
import os
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import time
from utils.logger_config import setup_logger

logger = setup_logger()

class ImagePreprocessor:
    def __init__(self, blur_type="median", thresh_type="otsu", min_thresh=127, max_thresh=255, noise_kernel=1, erode_kernel=2, dilate_kernel=2, noise_iter=1, erode_iter=1, dilate_iter=1):
        self.blur_type = blur_type
        self.thresh_type = thresh_type
        self.min_thresh = min_thresh
        self.max_thresh = max_thresh
        self.noise_kernel = noise_kernel
        self.erode_kernel = erode_kernel
        self.dilate_kernel = dilate_kernel
        self.noise_iter = noise_iter
        self.erode_iter = erode_iter
        self.dilate_iter = dilate_iter

    def update_args(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def grayscale(self, image):
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def binarization(self, image, blur_type, thresh_type, min_thresh, max_thresh):
        if blur_type == "median":
            image = cv2.medianBlur(image, 5)
        elif blur_type == "gaussian":
            image = cv2.GaussianBlur(image, (5, 5), 0)
        else:
            pass
            
        if thresh_type == "otsu":
            _, image = cv2.threshold(image, min_thresh, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        elif thresh_type == "adaptive":
            image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        else:  # binary
            _, image = cv2.threshold(image, min_thresh, max_thresh, cv2.THRESH_BINARY)
        
        return image

    def noise_removal(self, image, kernel_size=1, iterations=1):
        if kernel_size < 1: return image
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        image = cv2.dilate(image, kernel, iterations=iterations)
        image = cv2.erode(image, kernel, iterations=iterations)
        return image

    def thin_font(self, image, kernel_size=2, iterations=1):
        if kernel_size < 1: return image
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.erode(image, kernel, iterations=iterations)

    def thick_font(self, image, kernel_size=2, iterations=1):
        if kernel_size < 1: return image
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.dilate(image, kernel, iterations=iterations)

    def remove_and_add_borders(self, image):
        # Remove borders
        contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnt = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(cnt)
        cropped = image[y:y+h, x:x+w]
        
        # Add borders dynamically based on image dimensions
        height, width = cropped.shape
        top = bottom = height // 10
        left = right = width // 10
        
        color = [0, 0, 0]
        image_with_border = cv2.copyMakeBorder(cropped, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
        
        return image_with_border

    def preprocess_single_image(self, image):
        gray_image = self.grayscale(image)
        bin_image = self.binarization(gray_image, self.blur_type, self.thresh_type, self.min_thresh, self.max_thresh)
        denoised_image = self.noise_removal(bin_image, self.noise_kernel, self.noise_iter)
        thin_image = self.thin_font(denoised_image, self.erode_kernel, self.erode_iter)
        thick_image = self.thick_font(thin_image, self.dilate_kernel, self.dilate_iter)
        final_image = self.remove_and_add_borders(thick_image)
        return final_image

    def preprocess_images(self, src_folder, dest_folder):
        with ThreadPoolExecutor() as executor:
            futures = []
            for filename in os.listdir(src_folder):
                if filename.endswith(('.png', '.jpg', '.jpeg', '.tiff')):
                    image_path = os.path.join(src_folder, filename)
                    dest_path = os.path.join(dest_folder, filename)
                    futures.append(executor.submit(self.process_single_image, image_path, dest_path))
            for future in futures:
                future.result()  # to raise any exception that occurred during processing

    def process_single_image(self, image_path, dest_path):
        image = cv2.imread(image_path)
        final_image = self.preprocess_single_image(image)
        cv2.imwrite(dest_path, final_image)

def main(args):
    preprocessor = ImagePreprocessor(args.blur_type, args.thresh_type, args.min_thresh, args.max_thresh, args.noise_kernel, args.erode_kernel, args.dilate_kernel, args.noise_iter, args.erode_iter, args.dilate_iter)

    logger.info("Preprocessing images...")
    start_time = time.time()
    if os.path.isdir(args.input_path):
        preprocessor.preprocess_images(args.input_path, args.output_dir)
    elif os.path.isfile(args.input_path):
        filename = os.path.basename(args.input_path)
        dest_path = os.path.join(args.output_dir, filename)
        preprocessor.process_single_image(args.input_path, dest_path)
    else:
        logger.error(f"Invalid input path: {args.input_path}")
    logger.info(f'Preprocessing from {args.input_path} to {args.output_dir} complete in {time.time() - start_time}.')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Preprocess images in a folder.')
    parser.add_argument('input_path', help='Path of the image or folder to process.')
    parser.add_argument('output_dir', help='Destination folder to store processed images.')
    parser.add_argument('--blur_type', choices=["median", "gaussian", "none"], default="median", help='Type of blur to apply.')
    parser.add_argument('--thresh_type', choices=["otsu", "adaptive", "binary"], default="otsu", help='Type of thresholding to apply.')
    parser.add_argument('--min_thresh', type=int, default=127, help='Minimum threshold value for binary thresholding.')
    parser.add_argument('--max_thresh', type=int, default=255, help='Maximum threshold value for binary thresholding.')
    parser.add_argument('--noise_kernel', type=int, default=1, help='Kernel size for noise removal. Skip if less than 1.')
    parser.add_argument('--erode_kernel', type=int, default=2, help='Kernel size for erosion. Skip if less than 1.')
    parser.add_argument('--dilate_kernel', type=int, default=2, help='Kernel size for dilation. Skip if less than 1.')
    parser.add_argument('--noise_iter', type=int, default=1, help='Iterations for noise removal.')
    parser.add_argument('--erode_iter', type=int, default=1, help='Iterations for erosion.')
    parser.add_argument('--dilate_iter', type=int, default=1, help='Iterations for dilation.')
    
    args = parser.parse_args()
    main(args)