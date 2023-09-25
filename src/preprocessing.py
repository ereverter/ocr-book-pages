import argparse
import cv2
import os
import numpy as np

def grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def binarization(image, blur_type, thresh_type, min_thresh, max_thresh):
    if blur_type == "median":
        image = cv2.medianBlur(image, 5)
    elif blur_type == "gaussian":
        image = cv2.GaussianBlur(image, (5, 5), 0)
        
    if thresh_type == "otsu":
        _, image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    elif thresh_type == "adaptive":
        image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    else:  # binary
        _, image = cv2.threshold(image, min_thresh, max_thresh, cv2.THRESH_BINARY)
    
    return image

def noise_removal(image, kernel_size=1, iterations=1):
    if kernel_size < 1: return image
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    image = cv2.dilate(image, kernel, iterations=iterations)
    image = cv2.erode(image, kernel, iterations=iterations)
    return image

def thin_font(image, kernel_size=2, iterations=1):
    if kernel_size < 1: return image
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    return cv2.erode(image, kernel, iterations=iterations)

def thick_font(image, kernel_size=2, iterations=1):
    if kernel_size < 1: return image
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    return cv2.dilate(image, kernel, iterations=iterations)

def remove_and_add_borders(image):
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

def preprocess_image(image, blur_type="median", thresh_type="otsu", min_thresh=127, max_thresh=255, noise_kernel=1, erode_kernel=2, dilate_kernel=2, noise_iter=1, erode_iter=1, dilate_iter=1):
    # Convert to grayscale
    gray_image = grayscale(image)
    
    # Binarization
    bin_image = binarization(gray_image, blur_type, thresh_type, min_thresh, max_thresh)
    
    # Noise Removal
    denoised_image = noise_removal(bin_image, noise_kernel, noise_iter)
    
    # Thin Font
    thin_image = thin_font(denoised_image, erode_kernel, erode_iter)
    
    # Thick Font
    thick_image = thick_font(thin_image, dilate_kernel, dilate_iter)
    
    # Remove and add borders
    final_image = remove_and_add_borders(thick_image)
    
    return final_image

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Preprocess images in a folder.')
    parser.add_argument('src_folder', help='Source folder containing images to be processed.')
    parser.add_argument('dest_folder', help='Destination folder to store processed images.')
    parser.add_argument('--blur_type', choices=["median", "gaussian"], default="median", help='Type of blur to apply.')
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
    
    for filename in os.listdir(args.src_folder):
        if filename.endswith(('.png', '.jpg', '.jpeg', '.tiff')):
            image_path = os.path.join(args.src_folder, filename)
            image = cv2.imread(image_path)
            
            # Preprocess image
            final_image = preprocess_image(image, args.blur_type, args.thresh_type, args.min_thresh, args.max_thresh, args.noise_kernel, args.erode_kernel, args.dilate_kernel, args.noise_iter, args.erode_iter, args.dilate_iter)
            
            dest_path = os.path.join(args.dest_folder, filename)
            cv2.imwrite(dest_path, final_image)
