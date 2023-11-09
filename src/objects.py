#!/usr/bin/env python3

class ProcessedImage:
    def __init__(self, original_img):
        self.original_img = original_img
        self.dewarped_img = None
        self.preprocessed_img = None
        self.extracted_text = None