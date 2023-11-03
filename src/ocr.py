#!/usr/bin/env python3
import os
import cv2
import argparse
import pytesseract
from concurrent.futures import ThreadPoolExecutor
from .utils.logger_config import setup_logger
import time

logger = setup_logger()

class TextExtractor:
    def __init__(self, lang='eng', nan_thresh=0.5):
        self.lang = lang
        self.nan_thresh = nan_thresh

    def update_args(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_text(self, img):
        df = pytesseract.image_to_data(img, lang=self.lang, output_type=pytesseract.Output.DATAFRAME)
        df = self._cleanup_block_paragraph(df, self.nan_thresh)
        df_filtered = df.dropna(subset=['text'])
        df_sorted = df_filtered.sort_values(by=['parent_group', 'line_num', 'word_num'])

        text = ""
        for _, group in df_sorted.groupby('parent_group'):
            words = group['text'].tolist()
            text += " ".join(words) + " "

        return text

    def _cleanup_block_paragraph(self, df, threshold=0.5):
        df['parent_group'] = self._get_word_group(df)
        df = df.groupby('parent_group').filter(lambda x: x.isnull().sum().sum() / x.shape[0] < threshold)
        return df

    def _get_word_group(self, df):
        return df['page_num'].astype(str) + '_' + df['block_num'].astype(str) + '_' + df['par_num'].astype(str)
    
    def process_single_image(self, image_path, output_dir):
        if os.path.exists(image_path) and image_path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff')):
            image = cv2.imread(image_path)
            extracted_text = self.get_text(image)
            output_filename = os.path.splitext(os.path.basename(image_path))[0] + '.txt'
            output_path = os.path.join(output_dir, output_filename)
            with open(output_path, 'w') as file:
                file.write(extracted_text)
        else:
            logger.info(f"{image_path} is not a valid image file.")

    def process_images(self, image_folder, output_dir):
        with ThreadPoolExecutor() as executor:
            for filename in os.listdir(image_folder):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff')):
                    image_path = os.path.join(image_folder, filename)
                    executor.submit(self.process_single_image, image_path, output_dir)

def main(args):
    text_extractor = TextExtractor(args.lang, args.nan_thresh)
    
    logger.info('Extracting text...')
    start_time = time.time()
    
    if os.path.isdir(args.input_path):
        text_extractor.process_images(args.input_path, args.output_dir)
    elif os.path.isfile(args.input_path):
        text_extractor.process_single_image(args.input_path, args.output_dir)
    else:
        logger.error(f"Invalid input path: {args.input_path}")
    logger.info(f'Extraction from {args.input_path} to {args.output_dir} complete in {time.time() - start_time}.')

def set_up_argparse():
    parser = argparse.ArgumentParser(description='Extract text from a given image path.')
    parser.add_argument('input_path', help='Path of the image or folder to process.')
    parser.add_argument('output_dir', help='Destination folder to store processed images.')
    parser.add_argument('--lang', default='eng', help='Language used by Tesseract. Default is English.')
    parser.add_argument('--nan_thresh', type=float, default=0.5, help='NaN threshold for cleanup.')
    return parser

if __name__ == "__main__":
    parser = set_up_argparse()
    args = parser.parse_args()
    main(args)