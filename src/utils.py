import cv2

def is_image_empty(image):
    return cv2.countNonZero(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)) == 0
