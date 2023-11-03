import argparse
from src.dewarping import set_up_argparse as set_up_argparse_dewarping, main as main_dewarping
from src.preprocessing import set_up_argparse as set_up_argparse_preprocessing, main as main_preprocessing
from src.ocr import set_up_argparse as set_up_argparse_ocr, main as main_ocr

def postprocessing_main(args):
    from src.postprocessing import set_up_argparse as set_up_argparse_postprocessing, main as main_postprocessing
    postprocess_parser = argparse.ArgumentParser(parents=[set_up_argparse_postprocessing()], add_help=False)
    postprocess_args = postprocess_parser.parse_args(args.remaining_args)
    main_postprocessing(postprocess_args)

def main():
    parser = argparse.ArgumentParser(description='OCR processing.')
    subparsers = parser.add_subparsers()

    dewarp_parser = subparsers.add_parser('dewarp', help='Dewarp images in a folder.', parents=[set_up_argparse_dewarping()],add_help=False)
    dewarp_parser.set_defaults(func=main_dewarping)

    preprocess_parser = subparsers.add_parser('preprocess', help='Preprocess images in a folder.', parents=[set_up_argparse_preprocessing()], add_help=False)
    preprocess_parser.set_defaults(func=main_preprocessing)

    ocr_parser = subparsers.add_parser('ocr', help='Extract text from images in a folder.', parents=[set_up_argparse_ocr()], add_help=False)
    ocr_parser.set_defaults(func=main_ocr)

    postprocess_parser = subparsers.add_parser('postprocess', help='Clean text files in a folder using an LLM.')
    postprocess_parser.set_defaults(func=postprocessing_main, remaining_args=None)
    
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()