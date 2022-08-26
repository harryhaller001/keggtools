# keggtools
Library for KEGG pathway enrichment analysis.

## Installation

`keggtools` only supports `python` version greater than or equal `3.6`.

Dependencies

* `graphviz`

`python` dependencies

* `requests`
* `pydot`
* `scipy>=1.5.4`


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

Run linting with `pylint` for `keggtools` package.

```bash
# Run linting for package
make pylint
```

### Static code analysis

Static code analysis using `mypy`. Run static code analysis with `mypy`.

```bash
# Run static code analysis
make mypy
```

### Testing

Run unittest for `keggtools` package.

```bash
# Run unittest for package
make pytest
```

### Install package from repo

The package is using the `flit` backend with a `pyproject.toml` and `twine`. To install from repo use

```bash
# Install package from repo
make twine
```
