import pytesseract

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
    """
    Given the output from tesseract, remove all paragraphs from each block that have more than threshold NaNs
    """
    # Get word group
    df['parent_group'] = _get_word_group(df)

    # Remove groups with more than threshold NaNs
    df = df.groupby('parent_group').filter(lambda x: x.isnull().sum().sum() / x.shape[0] < threshold)
    return df

def _get_word_group(df):
    return df['page_num'].astype(str) + '_' + df['block_num'].astype(str) + '_' + df['par_num'].astype(str)
