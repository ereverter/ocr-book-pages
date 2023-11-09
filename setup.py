#!/usr/bin/env python3
from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read()

setup(
    name="ocr-book-pages",
    version="1.0.0",
    author="Enric Reverter",
    author_email="ereverter.ds@gmail.com",
    description="Batch OCR for book pages pictures.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/eReverter/ocr-book-pages",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "ocr-book-pages = src.__main__:main",
        ],
    },
)