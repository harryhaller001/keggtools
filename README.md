# keggtools
Library for KEGG pathway enrichment analysis.

## Installation

`keggtools` only supports `python` version greater than or equal `3.6`.

Dependencies

* `graphviz`

`python` dependencies

* `requests`
* `tqdm`
* `pydot`
* `scipy`

Installation of `python` dependencies:

```bash
python3 -m pip install requests tqdm pydot scipy
```


Installation `keggtools` package using `pip`:

```bash
python3 -m pip install keggtools
```

To get a more detailed list of install options, please read the `INSTALL.md`

## API

### Download and Parsing


```python
from keggtools.resolver import KEGGPathwayResolver
from keggtools.const import IMMUNE_SYSTEM_PATHWAYS

ORGANISM_ID = "hsa"
resolver = KEGGPathwayResolver(org=ORGANISM_ID)

# Select first immune system pathway as example
pathway_id = list(IMMUNE_SYSTEM_PATHWAYS.keys())[1]

# Resolve pathway
pathway = resolver.get_pathway(code=pathway_id)
print(pathway)
```


### Enrichment and Testing

```python
from keggtools.analysis import KEGGPathwayAnalysis

# Init analysis with organism code
analysis = KEGGPathwayAnalysis(org=ORGANISM_ID)

# Study genes as list of entrez gene id's
study_genes = []
analysis.run_analysis(gene_list=study_genes)

# to_dataframe method requires pandas installation
result = analysis.to_dataframe()
print(result.head())
```

### Rendering

```python
import pydot
from keggtools.render import KEGGPathwayRenderer

# Load and parse pathway
pathway = KEGGPathwayResolver(org=ORGANISM_ID).get_pathway(pathway_id)
renderer = KEGGPathwayRenderer(kegg_pathway=pathway)

# Render to dot graph
dot_string = renderer.raw_render()

# Export dot graph as png
graphs = pydot.graph_from_dot_data(dot_string)[0]
graph.write_png("./output.png")
```

## Development

### Dev installation

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
# Install pytest
python3 -m pip install pytest

# Run unittest for package
pytest -p keggtools --show-capture=log
```

Alternatively, the `Makefile` can be used:

```bash
make unittest
```

### Static code analysis

Static code analysis using `mypy`

```bash
# Install mypy
python3 -m pip install mypy

# Or install full development requirements
pip install -r dev_requirements.txt
```

Run static code analysis with `mypy`

```bash
mypy setup.py
python3 setup.py install
mypy -p keggtools
```

