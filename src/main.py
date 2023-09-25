#usr/bin/env python3
import streamlit as st
import cv2
import os
import time
from dewarping import dewarp_single_image as dewarp_image
from preprocessing import preprocess_image
from ocr import get_text
import numpy as np
import tempfile

# Initialize session state variables if not already done
if 'original_img' not in st.session_state:
    st.session_state['original_img'] = None
    st.session_state['dewarped_img'] = None
    st.session_state['preprocessed_img'] = None
    st.session_state['extracted_text'] = None

def main():
    st.title("OCR Pipeline")
    st.sidebar.header("Processing Steps")
    processing_mode = st.selectbox("Processing Mode", ["Single Image", "Bulk Images"], key='processing_mode_select')

    if processing_mode == "Single Image":
        uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'png', 'jpeg', 'tiff'])

        if uploaded_file:
            image = cv2.imdecode(np.frombuffer(uploaded_file.read(), np.uint8), -1)
            st.session_state.original_img = image

            # Create placeholders here
            col11, col12 = st.columns([2, 3])  # 2:3 ratio for image and text
            with col11:
                image_placeholder = st.empty()
                image_placeholder.image(image, caption=f"original_img", use_column_width='auto')
                available_options = ['original_img', 'dewarped_img', 'preprocessed_img']
                selection = st.selectbox("Choose to display:", available_options, key=f'display_select')
                update_image_based_on_selection(image_placeholder, selection)
            with col12:
                text_placeholder = st.empty()

            dewarp_step(image_placeholder, text_placeholder)
            preprocess_step(image_placeholder, text_placeholder)
            ocr_step(image_placeholder, text_placeholder)

def update_image_based_on_selection(image_placeholder, selection):
    if st.session_state[selection] is not None:
        image_placeholder.image(st.session_state[selection], caption=f"{selection}", use_column_width='auto')

def update_text(text_placeholder, text):
    text_placeholder.empty()
    text_placeholder.write(text)

def dewarp_step(image_placeholder, text_placeholder):
    dewarp_button_state = st.sidebar.button("Dewarp", key="dewarp-btn")
    with st.sidebar.expander("1. Dewarping Options"):
        
        # With default value and placeholder
        page_margin_x = st.text_input("Page Margin X", value="25", placeholder="25")
        page_margin_y = st.text_input("Page Margin Y", value="25", placeholder="25")

        # Text area for additional args with example in placeholder
        additional_args_str = st.text_area("Additional Arguments", placeholder="-z 0")

        if dewarp_button_state:
            
            # Parse additional arguments from text_area
            additional_args_list = additional_args_str.split()
            
            additional_args = [
                "-x", page_margin_x,
                "-y", page_margin_y,
            ] + additional_args_list

            with tempfile.TemporaryDirectory() as tmpdirname:
                temp_image_path = os.path.join(tmpdirname, "temp_image.png")
                cv2.imwrite(temp_image_path, st.session_state['original_img'])
                
                original_dir = os.getcwd()
                os.chdir(tmpdirname)

                dewarp_image("temp_image.png", additional_args=additional_args) 
                
                os.chdir(original_dir)
                
                dewarped_image_path = os.path.join(tmpdirname, "temp_image_thresh.png")
                
                if os.path.exists(dewarped_image_path):
                    dewarped_img = cv2.imread(dewarped_image_path)
                    
                    if dewarped_img is not None:
                        st.session_state.dewarped_img = dewarped_img  # Save to session_state
                    else:
                        st.error("Could not read the dewarped image.")
                else:
                    st.error(f"Output image at {dewarped_image_path} does not exist.")

            if dewarped_img is not None:
                st.session_state.dewarped_img = dewarped_img  # Save to session_state
                update_image_based_on_selection(image_placeholder, 'dewarped_img')

def preprocess_step(image_placeholder, text_placeholder):
    preprocess_button_state = st.sidebar.button("Preprocess", key="preprocess-btn")
    with st.sidebar.expander("2. Preprocessing Options"):
        
        blur_type_arg = st.selectbox("Blur Type", ["median", "gaussian"])
        thresh_type_arg = st.selectbox("Threshold Type", ["otsu", "adaptive", "binary"])
        
        min_thresh_arg = st.slider("Minimum Threshold", min_value=0, max_value=255, value=127)
        max_thresh_arg = st.slider("Maximum Threshold", min_value=0, max_value=255, value=255)
        
        noise_kernel_arg = st.number_input("Noise Kernel Size", min_value=0, value=1)
        erode_kernel_arg = st.number_input("Erode Kernel Size", min_value=0, value=2)
        dilate_kernel_arg = st.number_input("Dilate Kernel Size", min_value=0, value=2)
        
        noise_iter_arg = st.number_input("Noise Removal Iterations", min_value=0, value=1)
        erode_iter_arg = st.number_input("Erosion Iterations", min_value=0, value=1)
        dilate_iter_arg = st.number_input("Dilation Iterations", min_value=0, value=1)
        
        if preprocess_button_state:
            preprocess_args = {
                "blur_type": blur_type_arg,
                "thresh_type": thresh_type_arg,
                "min_thresh": min_thresh_arg,
                "max_thresh": max_thresh_arg,
                "noise_kernel": noise_kernel_arg,
                "erode_kernel": erode_kernel_arg,
                "dilate_kernel": dilate_kernel_arg,
                "noise_iter": noise_iter_arg,
                "erode_iter": erode_iter_arg,
                "dilate_iter": dilate_iter_arg
            }

            # Call your preprocess_image function here
            preprocessed_image = preprocess_image(st.session_state.dewarped_img, **preprocess_args)
    
            if preprocessed_image is not None:
                st.session_state.preprocessed_img = preprocessed_image  # Save to session_state
                update_image_based_on_selection(image_placeholder, 'preprocessed_img')

def ocr_step(image_placeholder, text_placeholder):
    ocr_button_state = st.sidebar.button("OCR", key="ocr-btn")
    with st.sidebar.expander("3. OCR Options"):
        
        lang_arg = st.text_input("OCR Language", value="eng")
        nan_thresh_arg = st.slider("NaN Threshold", min_value=0.0, max_value=1.0, value=0.5, step=0.1)
        
        if ocr_button_state:
            ocr_args = {
                "lang": lang_arg,
                "nan_thresh": nan_thresh_arg
            }

            # Call your get_text function here
            extracted_text = get_text(st.session_state.preprocessed_img, **ocr_args)
            
            if extracted_text is not None:
                st.session_state.extracted_text = extracted_text  # Save to session_state
                update_text(text_placeholder, extracted_text)

if __name__ == "__main__":
    main()