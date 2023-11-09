#usr/bin/env python3
import streamlit as st
import cv2
import os
from src.dewarping import ImageDewarper
from src.preprocessing import ImagePreprocessor
from src.ocr import TextExtractor
from src.objects import ProcessedImage
import numpy as np
import tempfile
import hashlib

ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))
HELP_PATH = os.path.join(ABSOLUTE_PATH, 'docs/help')

class SingleOCR:
    """
    Class to orchestrate the OCR pipeline within the app.
    """
    def __init__(self):
        self.image_dewarper = ImageDewarper()
        self.image_preprocessor = ImagePreprocessor()
        self.text_extractor = TextExtractor()

    def run_dewarp(self, ui_handler, ui):
        # Avoid unnecessary computation if dewarp button is not pressed
        if not ui.dewarp_button_state:
            return

        # Dewarp the image and temporarily save it to a temp directory (mandatory for page-dewarp)
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Write the image to the temp directory
            temp_image_path = os.path.join(tmpdirname, "temp_image.png")
            cv2.imwrite(temp_image_path, ui_handler.processed_image.original_img)
            
            original_dir = os.getcwd()
            os.chdir(tmpdirname)

            # Dewarp the image
            self.image_dewarper.dewarp_single_image("temp_image.png", additional_args=ui.get_args()) 
            
            # Read the dewarped image that got saved to the temp directory
            os.chdir(original_dir)
            dewarped_image_path = os.path.join(tmpdirname, "temp_image_thresh.png")
            
            # Error handling
            if os.path.exists(dewarped_image_path):
                dewarped_img = cv2.imread(dewarped_image_path)
                
                if dewarped_img is not None:
                    ui_handler.processed_image.dewarped_img = dewarped_img  # Save to image object
                else:
                    st.error("Could not read the dewarped image.")
            else:
                st.error(f"Output image at {dewarped_image_path} does not exist.")

        # Update the depicted image
        if dewarped_img is not None:
            ui_handler.update_image_based_on_selection('dewarped_img')
    
    def run_preprocess(self, ui_handler, ui):
        # Avoid unnecessary computation if preprocess button is not pressed
        if not ui.preprocess_button_state:
            return
    
        # Actually preprocess the image
        self.image_preprocessor.update_args(**ui.get_args())
        image_to_preprocess = ui_handler.processed_image.dewarped_img if ui_handler.processed_image.dewarped_img is not None else ui_handler.processed_image.original_img
        preprocessed_image = self.image_preprocessor.preprocess_single_image(image_to_preprocess)

        # Update the depicted image
        if preprocessed_image is not None:
            ui_handler.processed_image.preprocessed_img = preprocessed_image  # Save to session_state
            ui_handler.update_image_based_on_selection('preprocessed_img')
    
    def run_ocr(self, ui_handler, ui):
        # Avoid unnecessary computation if ocr button is not pressed
        if not ui.ocr_button_state:
            return

        # Call your get_text function here
        self.text_extractor.update_args(**ui.get_args())
        image_to_use = None
        if ui_handler.processed_image.preprocessed_img is not None:
            image_to_use = ui_handler.processed_image.preprocessed_img
        elif ui_handler.processed_image.dewarped_img is not None:
            image_to_use = ui_handler.processed_image.dewarped_img
        elif ui_handler.processed_image.original_img is not None:
            image_to_use = ui_handler.processed_image.original_img

        if image_to_use is not None:
            extracted_text = self.text_extractor.get_text(image_to_use)
        else:
            st.error("No image available for OCR.")

        # Update depicted text
        if extracted_text is not None:
            ui_handler.processed_image.extracted_text = extracted_text
            ui_handler.update_text(extracted_text)
    
class BatchOCR:
    """WIP"""
    pass

class UIHandler:
    """
    Class to handle the main UI.
    """
    def __init__(self):
        if 'processed_image' not in st.session_state:
            st.session_state['processed_image'] = None
        
        if 'show_dewarp_help' not in st.session_state:
            st.session_state['show_dewarp_help'] = False
        
        if 'show_preprocess_help' not in st.session_state:
            st.session_state['show_preprocess_help'] = False
        
        if 'show_ocr_help' not in st.session_state:
            st.session_state['show_ocr_help'] = False

    @property
    def processed_image(self):
        return st.session_state['processed_image']
    
    @processed_image.setter
    def processed_image(self, value):
        st.session_state['processed_image'] = value 

    def handle_file_upload(self):
        uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'png', 'jpeg', 'tiff'])

        if uploaded_file is not None:
            current_file_hash = self._get_file_hash(uploaded_file)
            previous_file_hash = st.session_state.get('file_hash', None)

            if previous_file_hash is None or previous_file_hash != current_file_hash:
                st.session_state['file_hash'] = current_file_hash  # Update the file hash in session state
                image = cv2.imdecode(np.frombuffer(uploaded_file.read(), np.uint8), -1)
                self.processed_image = ProcessedImage(image)  # Save the image to UIHandler instance

            return True  # File was uploaded
        return False  # No file uploaded
    
    def _get_file_hash(self, uploaded_file):
        file_hash = hashlib.md5(uploaded_file.read()).hexdigest()
        uploaded_file.seek(0)  # Reset file pointer to the beginning
        return file_hash
    
    def handle_img_text(self):
        col1, col2 = st.columns([2, 3])  # 2:3 ratio for image and text
        self.image_placeholder = col1.empty()
        self.text_placeholder = col2.empty()
        self.available_options = ['original_img', 'dewarped_img', 'preprocessed_img']
        self.selection = col1.selectbox("Choose to display:", self.available_options, key=f'display_select')

    def update_image_based_on_selection(self, selection):
        image_to_display = getattr(self.processed_image, selection)
        if image_to_display is not None:
            self.image_placeholder.image(image_to_display, caption=f"{selection}", use_column_width='auto')

    def update_text(self, text):
        self.text_placeholder.empty()
        self.text_placeholder.write(text)

    def control_spinner(self, action):
        if action == 'start':
            self.spinner_placeholder.spinner("Processing...")
        elif action == 'stop':
            self.spinner_placeholder.empty()

class DewarpUI:
    """Class to handle the dewarping UI."""
    def __init__(self):
        col1, col2 = st.sidebar.columns([1, 0.2])
        self.dewarp_button_state = col1.button("Dewarp", key="dewarp-btn", type="primary")
        self.help_button_state = col2.button("?", key="dewarp-help-btn")

        if self.help_button_state:
            st.session_state['show_dewarp_help'] = not st.session_state.get('show_dewarp_help', False)

        if st.session_state.get('show_dewarp_help', False):
            with open(f'{HELP_PATH}/dewarp.txt', 'r') as file:
                help_text = file.read()
            st.sidebar.info(help_text)

        with st.sidebar.expander("1. Dewarping Options"):
            self.page_margin_x = st.text_input("Page Margin X", value="25", placeholder="25")
            self.page_margin_y = st.text_input("Page Margin Y", value="25", placeholder="25")
            self.additional_args_str = st.text_area("Additional Arguments", placeholder="-z 0")

    def get_args(self):
        args = ["-x", self.page_margin_x, 
                "-y", self.page_margin_y,
                ] + self.additional_args_str.split()
        return args

class PreprocessUI:
    """Class to handle the preprocessing UI."""
    def __init__(self):
        col1, col2 = st.sidebar.columns([1, 0.2])
        self.preprocess_button_state = col1.button("Preprocess", key="preprocess-btn", type="primary")
        self.help_button_state = col2.button("!?", key="preprocess-help-btn")

        if self.help_button_state:
            st.session_state['show_preprocess_help'] = not st.session_state.get('show_preprocess_help', False)

        if st.session_state['show_preprocess_help']:
            with open(f'{HELP_PATH}/preprocess.txt', 'r') as file:
                help_text = file.read()
            st.sidebar.info(help_text)

        with st.sidebar.expander("2. Preprocessing Options"):
            self.blur_type_arg = st.selectbox("Blur Type", ["gaussian", "median", "none"])
            self.thresh_type_arg = st.selectbox("Threshold Type", ["binary", "otsu", "adaptive"])
            
            self.min_thresh_arg = st.slider("Minimum Threshold", min_value=0, max_value=255, value=127)
            self.max_thresh_arg = st.slider("Maximum Threshold", min_value=0, max_value=255, value=255)
            
            self.noise_kernel_arg = st.number_input("Noise Kernel Size", min_value=0, value=1)
            self.noise_iter_arg = st.number_input("Noise Removal Iterations", min_value=0, value=1)
            
            self.erode_kernel_arg = st.number_input("Erode Kernel Size", min_value=0, value=0)
            self.erode_iter_arg = st.number_input("Erosion Iterations", min_value=0, value=1)
            
            self.dilate_kernel_arg = st.number_input("Dilate Kernel Size", min_value=0, value=0)
            self.dilate_iter_arg = st.number_input("Dilation Iterations", min_value=0, value=1)

    def get_args(self):
        args = {
            "blur_type": self.blur_type_arg,
            "thresh_type": self.thresh_type_arg,
            "min_thresh": self.min_thresh_arg,
            "max_thresh": self.max_thresh_arg,
            "noise_kernel": self.noise_kernel_arg,
            "erode_kernel": self.erode_kernel_arg,
            "dilate_kernel": self.dilate_kernel_arg,
            "noise_iter": self.noise_iter_arg,
            "erode_iter": self.erode_iter_arg,
            "dilate_iter": self.dilate_iter_arg
        }

        return args
    

class OCRUI:
    """Class to handle the OCR UI."""
    def __init__(self):
        col1, col2 = st.sidebar.columns([1, 0.2])
        self.ocr_button_state = col1.button("OCR", key="ocr-btn", type="primary")
        self.help_button_state = col2.button("?", key="ocr-help-btn")

        if self.help_button_state:
            st.session_state['show_ocr_help'] = not st.session_state.get('show_ocr_help', False)
        
        if st.session_state['show_ocr_help']:
            with open(f'{HELP_PATH}/ocr.txt', 'r') as file:
                help_text = file.read()
            st.sidebar.info(help_text)

        with st.sidebar.expander("3. OCR Options"):
            self.lang_option = st.selectbox("Language", ["eng", "cat", "Other"])
            if self.lang_option == "Other":
                self.lang_arg = st.text_input("Enter language")
            else:
                self.lang_arg = self.lang_option
            self.nan_thresh_arg = st.slider("NaN Threshold", min_value=0.0, max_value=1.0, value=0.5, step=0.05)

    def get_args(self):
        args = {
            "lang": self.lang_arg,
            "nan_thresh": self.nan_thresh_arg
        }

        return args

def main():
    st.title("OCR Pipeline")

    # Instantiate the UI handler and the OCR orchestrator
    ui_handler = UIHandler()
    single_ocr = SingleOCR()

    # Handle file upload
    if ui_handler.handle_file_upload():
        st.sidebar.header("Processing Steps")
        status_placeholder = st.sidebar.empty()

        # If a file is uploaded, handle the image and text UI
        ui_handler.handle_img_text()
        ui_handler.update_image_based_on_selection(ui_handler.selection)
        if ui_handler.processed_image.extracted_text is None:
            ui_handler.update_text("Your text will appear here.")
        else:
            ui_handler.update_text(ui_handler.processed_image.extracted_text)

        # Instantiate the UI for each step in the pipeline
        dewarp_ui = DewarpUI()
        preprocess_ui = PreprocessUI()
        ocr_ui = OCRUI()

        if dewarp_ui.dewarp_button_state:
            status_placeholder.text("Running Dewarp...")
            single_ocr.run_dewarp(ui_handler, dewarp_ui)
            status_placeholder.empty()

        if preprocess_ui.preprocess_button_state:
            status_placeholder.text("Running Preprocess...")
            single_ocr.run_preprocess(ui_handler, preprocess_ui)
            status_placeholder.empty()

        if ocr_ui.ocr_button_state:
            status_placeholder.text("Running OCR...")
            single_ocr.run_ocr(ui_handler, ocr_ui)
            status_placeholder.empty()

# Call the main function to run the app
if __name__ == "__main__":
    main()
