
# Dependencies

To fulfill all dependencies for this project, **all** of the following steps are required.
`keggtools` only supports `python` version greater than or equal `3.6`.

## Step 1: Install graphviz

Dependencies

* `graphviz`

Install graphviz on `Ubuntu`. More graphviz install options [https://www.graphviz.org/download/](https://www.graphviz.org/download/)

```bash
# pydot is needed for rendering of pathways and required graphviz
sudo apt install graphviz
```

## Step 2: Install python dependencies

Python dependencies

* `requests`
* `pydot`
* `scipy`

Installation of `python` dependencies:

```bash
python3 -m pip install requests pydot scipy
```

# Installation for `keggtools`

Choose **one** option to install this package

## Option 1: Install from `pypi` (recommended)

Installation `keggtools` package using `pip`:

```bash
python3 -m pip install keggtools
```

## Option 2: Install from release source

Installation `keggtools` from source:

```bash
# Clone repo
git clone https://github.com/harryhaller001/keggtools.git
cd keggtools

# Install dependencies and package
python3 -m pip install -r requirements.txt
python3 setup.py install
```


## Option 3: Install from github source


Installation `keggtools` from Github source:

```bash
python3 -m pip install git+git@github.com:harryhaller001/keggtools.git
```

