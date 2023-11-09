#!/usr/bin/env python3
import json
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import argparse
import os
import time
from .utils.logger_config import setup_logger

logger = setup_logger()

class TextCleanerLLM:
    """
    Super-simple text cleaner for OCR results using an LLM.
    """

    def __init__(self, model_name_or_path="TheBloke/Mistral-7B-Instruct-v0.1-GPTQ",
                 device_map="auto",
                 trust_remote_code=False,
                 revision="main",
                 use_fast=True,
                 prompt_template=None,
                 pipeline_params=None):

        self.model = AutoModelForCausalLM.from_pretrained(model_name_or_path,
                                                          device_map=device_map,
                                                          trust_remote_code=trust_remote_code,
                                                          revision=revision)

        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, use_fast=use_fast)

        self.pipeline_params = pipeline_params or {
            'max_new_tokens': 512,
            'do_sample': True,
            'temperature': 0.7,
            'top_p': 0.95,
            'top_k': 40,
            'repetition_penalty': 1.1
        }

        self.pipe = pipeline("text-generation",
                             model=self.model,
                             tokenizer=self.tokenizer,
                             **self.pipeline_params)

        self.prompt_template = prompt_template

    def update_pipeline_params(self, new_params):
        self.pipeline_params.update(new_params)
        self.pipe = pipeline("text-generation",
                             model=self.model,
                             tokenizer=self.tokenizer,
                             return_full_text=False,
                             **self.pipeline_params)

    def set_prompt_template(self, prompt_template_file): ###
        if not os.path.exists(prompt_template_file):
            logger.error(f"Prompt template file {prompt_template_file} does not exist.")
            return
        with open(prompt_template_file, 'r') as f:
            prompt_template = json.load(f)
        self.prompt_template = prompt_template['messages']

    def clean_text(self, text): ###
        if self.prompt_template is None:
            prompt_template = [{'role': 'user', 'content': text}]
        else:
            prompt_template = self.prompt_template.copy()
            prompt_template[-1]['content'] = prompt_template[-1]['content'].format(text=text)
        
        prompt = self.tokenizer.decode(self.tokenizer.apply_chat_template(prompt_template, return_tensors="pt")[0])
        return self.pipe(prompt)[0]['generated_text']

def main(args):
    logger.info("Loading LLM...")
    cleaner = TextCleanerLLM()
    if args.prompt_template is not None:
        cleaner.set_prompt_template(args.prompt_template)

    logger.info("Cleaning text...")
    start_time = time.time()

    if os.path.isdir(args.input_path):
        for filename in os.listdir(args.input_path):
            if filename.endswith('.txt'):
                file_path = os.path.join(args.input_path, filename)
                with open(file_path, 'r') as file:
                    text = file.read()
                    cleaned_text = cleaner.clean_text(text)
                    output_file_path = os.path.join(args.output_dir, filename)
                    with open(output_file_path, 'w') as outfile:
                        outfile.write(cleaned_text)

    elif os.path.isfile(args.input_path) and args.input_path.endswith('.txt'):
        with open(args.input_path, 'r') as file:
            text = file.read()
            cleaned_text = cleaner.clean_text(text)
            output_filename = os.path.basename(args.input_path)
            output_file_path = os.path.join(args.output_dir, output_filename)
            with open(output_file_path, 'w') as outfile:
                outfile.write(cleaned_text)
    else:
        logger.error(f"Invalid input path: {args.input_path}")

    logger.info(f'Cleaning from {args.input_path} to {args.output_dir} complete in {time.time() - start_time}.')

def parser_add_arguments(parser):
    parser.add_argument('input_path', help='Path of the text file or folder to process.')
    parser.add_argument('output_dir', help='Destination folder to store processed text.')
    parser.add_argument('--prompt_template', required=True, help='Path to prompt template file.') ### 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process text files using TextCleanerLLM.')
    parser_add_arguments(parser)
    args = parser.parse_args()
    main(args)