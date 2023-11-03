import argparse
from src.dewarping import main as main_dewarping
from src.preprocessing import main as main_preprocessing
from src.ocr import main as main_ocr

def postprocessing_main(args):
    from src.postprocessing import main as main_postprocessing
    main_postprocessing(args)

def main():
    parser = argparse.ArgumentParser(description='OCR processing.')
    subparsers = parser.add_subparsers()

    dewarp_parser = subparsers.add_parser('dewarp', help='Dewarp images in a folder.')
    dewarp_parser.set_defaults(func=main_dewarping)
    
    preprocess_parser = subparsers.add_parser('preprocess', help='Preprocess images in a folder.')
    preprocess_parser.set_defaults(func=main_preprocessing)

    ocr_parser = subparsers.add_parser('ocr', help='Extract text from images in a folder.')
    ocr_parser.set_defaults(func=main_ocr)

    postprocess_parser = subparsers.add_parser('postprocess', help='Clean text files in a folder using an LLM.')
    postprocess_parser.set_defaults(func=postprocessing_main)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()