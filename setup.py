""" Python Installation file """

import os
from distutils.core import setup
import setuptools


def read(fname: str):
    """
    Read file content of given filename
    """
    return open(os.path.join(os.path.dirname(__file__), fname), mode="r", encoding="utf-8").read()

setup(
    name = "keggtools",
    version = "0.5.0",
    license="MIT",
    author = "harryhaller001",
    author_email = "harryhaller001@gmail.com",
    description = ("Enrichment analysis and visualisation toolkit for KEGG pathways"),
    packages=setuptools.find_packages(),
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    url="https://github.com/harryhaller001/keggtools",
    install_requires=[
        "requests",
        "pydot",
        "scipy"
    ],
    # download_url="https://github.com/harryhaller001/keggtools" # TODO: add release
)
