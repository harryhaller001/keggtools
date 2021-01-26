
import os
import setuptools
from distutils.core import setup

def read(fname: str):
    return open(os.path.join(os.path.dirname(__file__), fname), encoding="utf-8").read()

setup(
    name = "keggtools",
    version = "0.2.0",
    author = "harryhaller001",
    author_email = "harryhaller001@gmail.com",
    description = ("Enrichment analysis and visualisation toolkit for KEGG pathways"),
    packages=setuptools.find_packages(), # ['keggtools'],
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    url="https://github.com/harryhaller001/keggtools"
)

