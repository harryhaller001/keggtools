
import os
from distutils.core import setup

def read(fname: str):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "keggtools",
    version = "0.1.0",
    author = "harryhaller001",
    author_email = "harryhaller001@gmail.com",
    description = ("Enrichment analysis and visualisation toolkit for KEGG pathways"),
    packages=['keggtools'],
    long_description=read('README.md'),
)

