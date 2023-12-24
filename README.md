# OCR Pipeline

[![Streamlit App](https://img.shields.io/badge/Streamlit-App-blue?style=for-the-badge&logo=Streamlit)](https://ocr-book-pages.streamlit.app/)                                        

## Overview

This is an OCR (Optical Character Recognition) pipeline for book pages. The steps include image dewarping, preprocessing, and OCR text extraction. There is a demo for single image processing and some languages deployed in Streamlit. It uses [page-dewarp](https://github.com/lmmx/page-dewarp), [opencv](https://github.com/opencv/opencv), and [tesseract](https://github.com/tesseract-ocr/tesseract) for each step. The batch processing within the app (locally deployed) is a work in progress. It can be done using commands, but the app does not have the interface for it yet.

![Pipeline](https://github.com/ereverter/ocr-book-pages/blob/main/images/pipeline.jpg)

## Features

- **Image Dewarping**: Corrects distortions in the uploaded image.
- **Image Preprocessing**: Applies various image processing techniques like blurring, thresholding, noise removal, etc.
- **OCR**: Utilizes Tesseract for text extraction.

## Installation

1. Clone this repository
    ```bash
    git clone https://github.com/ereverter/ocr-book-pages.git
    ```

2. Navigate to the project directory and install dependencies
    ```bash
    cd ocr-book-pages
    pip install -r requirements.txt
    ```

3. Make sure you have Tesseract installed and the following apt packages for Debian-based systems:

    ```bash
    apt-get libgl1-mesa-glx
    apt-get libglib2.0-0
    apt-get tesseract-ocr
    ```

   To install specific languages use:
   ```bash
   apt-get tesseract-ocr-cat
   ```
   To install all at once:
   ```bash
   apt-get tesseract-ocr-all
   ```
   
## Usage

Run the following command to start the Streamlit app:
```bash
streamlit run app.py
```

## Work In Progress
- [x] Demo
- [x] Batch processing
- [x] Clean extracted text using an LLM
    - [ ] Refactor code and improve prompts
- [ ] Automatically set the preprocessing parameters given an input
