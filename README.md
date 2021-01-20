# keggtools
Library for KEGG pathway enrichment analysis

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
* `scipy` (Needed?)

Installation of python dependencies:

```bash
python3 -m pip install requests tqdm pydot scipy
```


Installation `keggtools` package using `pip`:

```bash
python3 -m pip install keggtools
```

Installation `keggtools` from github source:

```bash
# ??? Not sure
python3 -m pip install git+git@github.com:harryhaller001/keggtools.git
```

Installation `keggtools` from release source:

```bash
# TODO add release
```

Run unittest to verify `keggtools` installation

```bash
# TODO: implement unittest
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

