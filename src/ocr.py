import os
import cv2
import argparse
import pytesseract

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract text from a given image path.')
    parser.add_argument('image_path', help='Path of the image to extract text from.')
    parser.add_argument('--lang', default='eng', help='Language used by Tesseract. Default is English.')
    parser.add_argument('--nan_thresh', type=float, default=0.5, help='NaN threshold for cleanup.')
    
    args = parser.parse_args()
    
    if os.path.exists(args.image_path) and args.image_path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff')):
        image = cv2.imread(args.image_path)
        text_extractor = TextExtractor(args.lang, args.nan_thresh)
        extracted_text = text_extractor.get_text(image)
        
        print("Extracted Text:")
        print(extracted_text)
    else:
        print(f"Invalid image path: {args.image_path}")
