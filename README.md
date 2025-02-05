# keggtools

[![Version](https://img.shields.io/pypi/v/keggtools)](https://pypi.org/project/keggtools/)
[![codecov](https://codecov.io/gh/harryhaller001/keggtools/graph/badge.svg?token=3VBDIALBLK)](https://codecov.io/gh/harryhaller001/keggtools)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/keggtools)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/harryhaller001/keggtools/testing.yml)


Library for KEGG pathway enrichment analysis.

Documentation: [https://keggtools.org/](https://keggtools.org/)

PyPi: [https://pypi.org/project/keggtools/](https://pypi.org/project/keggtools/)


## Installation

`keggtools` only supports `python` version greater than or equal `3.8`.

Dependencies

* `graphviz`

`python` dependencies

* `requests`
* `pydot`
* `scipy`


Installation `keggtools` package using `pip`:

```bash
python3 -m pip install keggtools
```

To get a more detailed list of install options, please read the `INSTALL.md`

## API

### Download and Parsing


```python
from keggtools import Resolver, IMMUNE_SYSTEM_PATHWAYS

ORGANISM_ID = "hsa"
resolver = Resolver()

# Select first immune system pathway as example
pathway_id = list(IMMUNE_SYSTEM_PATHWAYS.keys())[1]

# Resolve pathway
pathway = resolver.get_pathway(organism=ORGANISM_ID, code=pathway_id)
print(pathway)
```


### Enrichment and Testing

```python
from keggtools import Enrichment

# Add pathway object to list
pathway_list = []

# Init analysis with organism code
analysis = Enrichment(pathways=pathway_list)

# Study genes as list of entrez gene id's
study_genes = []
analysis.run_analysis(gene_list=study_genes)

# to_dataframe method requires pandas installation
result = analysis.to_dataframe()
print(result.head())
```

### Rendering

```python
from keggtools.render import Renderer

# Load and parse pathway
renderer = Renderer(kegg_pathway=pathway)

# Render to dot graph
renderer.render()

# Export to png
renderer.to_file("output.png", extension="png")
```

## Development

### Dev installation

Fast install with `virtualenv` for development.

```bash
python3 -m virtualenv venv
source ./venv/bin/activate
pip install --upgrade pip

# Install from requirements
pip install -r requirements.txt

# Or use makefile
make install
```



### Linting

`ruff` is used for linting and formatting.

```bash
# Run formatter
make format
```

### Static code analysis

Static code analysis using `mypy`.

```bash
# Run static code analysis
make typing
```

### Testing

Run unittest for `keggtools` package. This uses `pytest` and `coverage`.

```bash
# Run unittest for package
make testing
```

### Install package from repo

The package is using the `flit` backend with a `pyproject.toml` and `twine`. To install from repo use

```bash
# Install package from repo
make build
```


### License

MIT
