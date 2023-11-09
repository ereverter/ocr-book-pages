import argparse
from src.dewarping import parser_add_arguments as parser_add_arguments_dewarping, main as main_dewarping
from src.preprocessing import parser_add_arguments as parser_add_arguments_preprocessing, main as main_preprocessing
from src.ocr import parser_add_arguments as parser_add_arguments_ocr, main as main_ocr

# Bandage to warn if LLM requirements are not installed and the user tries to use it
try:
    from src.postprocessing import parser_add_arguments as parser_add_arguments_postprocessing, main as main_postprocessing
    epilog = ""
except ImportError:
    epilog = "*** Note: Postprocessing is not enabled as LLM requirements are not installed. ***"
    parser_add_arguments_postprocessing = lambda x: None
    main_postprocessing = lambda x: None

def main():
    parser = argparse.ArgumentParser(description='OCR processing.')
    subparsers = parser.add_subparsers()

    dewarp_parser = subparsers.add_parser('dewarp', help='Dewarp images in a folder.')
    parser_add_arguments_dewarping(dewarp_parser)
    dewarp_parser.set_defaults(func=main_dewarping)

    preprocess_parser = subparsers.add_parser('preprocess', help='Preprocess images in a folder.')
    parser_add_arguments_preprocessing(preprocess_parser)
    preprocess_parser.set_defaults(func=main_preprocessing)

    ocr_parser = subparsers.add_parser('ocr', help='Extract text from images in a folder.')
    parser_add_arguments_ocr(ocr_parser)
    ocr_parser.set_defaults(func=main_ocr)

    postprocess_parser = subparsers.add_parser('postprocess', help='Clean text files in a folder using an LLM.', epilog=epilog)
    parser_add_arguments_postprocessing(postprocess_parser)
    postprocess_parser.set_defaults(func=main_postprocessing)    

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
