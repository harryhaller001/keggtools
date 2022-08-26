
# Declare global variables

PACKAGE_NAME	= keggtools

BASE_DIR		= ${PWD}

PYTHON_OPT		= python3
PIP_OPT			= $(PYTHON_OPT) -m pip
MYPY_OPT		= $(PYTHON_OPT) -m mypy
LINT_OPT		= $(PYTHON_OPT) -m pylint
TEST_OPT		= $(PYTHON_OPT) -m pytest
TWINE_OPT		= $(PYTHON_OPT) -m twine
SPHINX_OPT		= $(PYTHON_OPT) -m sphinx
COVERAGE_OPT	= $(PYTHON_OPT) -m coverage
FLIT_OPT		= $(PYTHON_OPT) -m flit

# Run help by default

.DEFAULT_GOAL := help


.PHONY: help
help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)




# Dependency handling

.PHONY: install
install: ## install all python dependencies
	@$(PIP_OPT) install mypy pylint pytest coverage twine setuptools types-requests responses flit pre-commit --upgrade
	@$(PIP_OPT) install requests scipy pydot pandas --upgrade
	@$(PIP_OPT) install Sphinx sphinx-rtd-theme --upgrade



.PHONY: freeze
freeze: ## Freeze package dependencies
	@$(PIP_OPT) freeze --exclude keggtools > requirements.txt



.PHONY: twine
twine: ## Twine package upload and checks

# Build package with flit backend
	@$(FLIT_OPT) build --setup-py

# Check package using twine
	@$(TWINE_OPT) check --strict ./dist/*

# Install package with flit
	@$(FLIT_OPT) install



.PHONY: pylint
pylint: ## Linting package
	@$(LINT_OPT) keggtools
	@$(LINT_OPT) ./test/*.py
	@$(LINT_OPT) ./docs/conf.py


.PHONY: pytest
pytest: ## Unittest of package
	@$(TEST_OPT) -p keggtools --show-capture=log


.PHONY: mypy
mypy: ## Run static code analysis
	@$(MYPY_OPT) ./test/*.py
	@$(MYPY_OPT) ./docs/conf.py
	@$(MYPY_OPT) -p keggtools




.PHONY: clean
clean: ## Clean all build and caching directories

# Remove old keggtools package
	@pip uninstall keggtools -y --quiet

# Remove package build folders
	@rm -rf ./build
	@rm -rf ./dist
	@rm -rf ./$(PACKAGE_NAME).egg-info

# Remove mypy and pytest caching folders
	@rm -rf ./.mypy_cache
	@rm -rf ./.pytest_cache
	@rm -rf ./coverage
	@rm -f .coverage

# Remove build folders for docs
	@rm -rf ./docs/_build
	@rm -rf ./docs/dist
	@rm -rf ./docs/cloudflare-workers/node_modules




.PHONY: docs
docs: ## Build sphinx docs
	@rm -rf ./docs/_build

# Generate dot graphics
	dot ./reproducibility/figures/figure1.dot -Tpng -Gdpi=300 > ./reproducibility/figures/figure1.png
	dot ./reproducibility/figures/figure5.dot -Tpng -Gdpi=300 > ./reproducibility/figures/figure5.png

# Copy figures to docs folder
	cp ./reproducibility/figures/figure1.png ./docs/media/kgml-schema.png
	cp ./reproducibility/figures/figure4.png ./docs/media/keggtools-enrichment.png
	cp ./reproducibility/figures/figure5.png ./docs/media/keggtools-pathway.png


	@$(SPHINX_OPT) -M doctest ./docs ./docs/_build
	@$(SPHINX_OPT) -M coverage ./docs ./docs/_build

# TODO: add latex pdf version of docs and copy to static files to include in HTML version
#	@$(SPHINX_OPT) -M latexpdf ./docs ./docs/_build && cp ./docs/_build/latex/keggtools.pdf ./docs/static/keggtools.pdf


# Build HTML version
	@$(SPHINX_OPT) -M html ./docs ./docs/_build





# Run all checks (always before committing!)
.PHONY: check
check: clean install freeze pylint mypy coverage twine docs precommit ## Full check of package




.PHONY : coverage
coverage: ## Run Coverage
	@$(COVERAGE_OPT) run -m pytest
	@$(COVERAGE_OPT) html --directory $(BASE_DIR)/coverage

# Long coverage report
	@$(COVERAGE_OPT) report -m



.PHONY : precommit
precommit: ## Run precommit file
	@pre-commit run --all-files --verbose


.PHONY : pdf
pdf: ## Generate Pdf file from latex

	cd ./reproducibility/latex; \
	biber paper; \
	pdflatex paper.tex

