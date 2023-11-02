#!/usr/bin/env python3
import json
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

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
                             **self.pipeline_params)

    def set_prompt_template(self, prompt_template_file):
        with open(prompt_template_file, 'r') as f:
            prompt_template = json.load(f)
        self.prompt_template = prompt_template['messages']

    def clean_text(self, text):
        if self.prompt_template is None:
            prompt_template = [{'content': text}]
        else:
            prompt_template = self.prompt_template.copy()
            prompt_template[-1]['content'] = prompt_template[-1]['content'].format(text=text)
        
        prompt = self.tokenizer.decode(self.tokenizer.apply_chat_template(prompt_template, return_tensors="pt")[0])
        return self.pipe(prompt)[0]['generated_text']