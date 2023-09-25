# import pytesseract

# def get_text(img, lang, nan_thresh=0.5):
#     df = pytesseract.image_to_data(img, lang=lang, output_type=pytesseract.Output.DATAFRAME)
#     df = cleanup_block_paragraph(df, nan_thresh)
#     df_filtered = df.dropna(subset=['text'])
#     df_sorted = df_filtered.sort_values(by=['parent_group', 'line_num', 'word_num'])

#     text = ""
#     for _, group in df_sorted.groupby('parent_group'):
#         words = group['text'].tolist()
#         text += " ".join(words) + " "

#     return text

# def cleanup_block_paragraph(df, threshold=0.5):
#     """
#     Given the output from tesseract, remove all paragraphs from each block that have more than threshold NaNs
#     """
#     # Get word group
#     df['parent_group'] = _get_word_group(df)

#     # Remove groups with more than threshold NaNs
#     df = df.groupby('parent_group').filter(lambda x: x.isnull().sum().sum() / x.shape[0] < threshold)
#     return df

# def _get_word_group(df):
#     return df['page_num'].astype(str) + '_' + df['block_num'].astype(str) + '_' + df['par_num'].astype(str)

import os
import cv2
import argparse
import pytesseract
import pandas as pd

def get_text(img, lang, nan_thresh=0.5):
    df = pytesseract.image_to_data(img, lang=lang, output_type=pytesseract.Output.DATAFRAME)
    df = cleanup_block_paragraph(df, nan_thresh)
    df_filtered = df.dropna(subset=['text'])
    df_sorted = df_filtered.sort_values(by=['parent_group', 'line_num', 'word_num'])

    text = ""
    for _, group in df_sorted.groupby('parent_group'):
        words = group['text'].tolist()
        text += " ".join(words) + " "

    return text

def cleanup_block_paragraph(df, threshold=0.5):
    df['parent_group'] = _get_word_group(df)
    df = df.groupby('parent_group').filter(lambda x: x.isnull().sum().sum() / x.shape[0] < threshold)
    return df

def _get_word_group(df):
    return df['page_num'].astype(str) + '_' + df['block_num'].astype(str) + '_' + df['par_num'].astype(str)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract text from a given image path.')
    parser.add_argument('image_path', help='Path of the image to extract text from.')
    parser.add_argument('--lang', default='eng', help='Language used by Tesseract. Default is English.')
    parser.add_argument('--nan_thresh', type=float, default=0.5, help='NaN threshold for cleanup.')
    
    args = parser.parse_args()
    
    if os.path.exists(args.image_path) and args.image_path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff')):
        image = cv2.imread(args.image_path)
        extracted_text = get_text(image, args.lang, args.nan_thresh)
        
        print("Extracted Text:")
        print(extracted_text)
    else:
        print(f"Invalid image path: {args.image_path}")
