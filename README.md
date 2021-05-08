# keggtools
Library for KEGG pathway enrichment analysis.

## Installation

`keggtools` only supports `python` version greater than or equal `3.6`.

Dependencies

* `graphviz`

Install graphviz on `Ubuntu`. More graphviz install options [https://www.graphviz.org/download/](https://www.graphviz.org/download/)
```bash
# pydot is needed for rendering of pathways and required graphviz
sudo apt install graphviz
```

Python dependencies

* `requests`
* `tqdm`
* `pydot`
* `scipy`

Installation of python dependencies:

```bash
python3 -m pip install requests tqdm pydot scipy
```


Installation `keggtools` PyPI package using `pip`:

```bash
python3 -m pip install keggtools
```

Installation `keggtools` from Github source:

```bash
python3 -m pip install git+git@github.com:harryhaller001/keggtools.git
```

Installation `keggtools` from release source:

```bash
# TODO add release
```


## API

### Download and caching


```python
from keggtools.resolver import KEGGPathwayResolver

# Get all components
print(KEGGPathwayResolver.get_components())

# List all pathways

# TODO: check taxid exists
organism_id = 10090

resolver = KEGGPathwayResolver(organism_id)

# TODO: maybe move to static methods
print(resolver.get_pathway_list())
```


### Parsing



### Enrichment and Testing



### Rendering


## Development

Fast install with `virtualenv` for development.

```bash
python3 -m virtualenv venv
source ./venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```



### Testing

Run unittest to verify `keggtools` installation

```bash
# TODO: implement unittest
```

### Static code analysis

Static code analysis using mypy

```bash
# Install mypy
pip install mypy

# Or
pip install -r dev_requirements.txt
```

Windows

```bash
# Testing setup.py and package
mypy setup.py
python setup.py install
# mypy --python-executable E:\Github\keggtools\venv\Scripts\python.exe -p keggtools --ignore-missing-imports
mypy -p keggtools
```

Linux

```bash
mypy setup.py
python3 setup.py install
mypy -p keggtools
```


## Build process

Build package

```bash
# Build .egg, .whl and .tar
python setup.py sdist bdist_wheel
```

