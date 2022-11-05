
# Declare global variables

PACKAGE_NAME	= keggtools

BASE_DIR		= ${PWD}

PACKAGE_DIR		= $(BASE_DIR)/$(PACKAGE_NAME)
TEST_DIR		= $(BASE_DIR)/test
DOCS_DIR		= $(BASE_DIR)/docs


PYTHON_OPT		= python3
PIP_OPT			= $(PYTHON_OPT) -m pip --require-virtualenv
MYPY_OPT		= $(PYTHON_OPT) -m mypy
FLAKE8_OPT		= $(PYTHON_OPT) -m flake8
BLACK_OPT		= $(PYTHON_OPT) -m black
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
	@$(PIP_OPT) install \
		mypy \
		flake8 \
		black \
		pytest \
		coverage \
		twine \
		setuptools \
		types-requests \
		responses \
		flit \
		pre-commit \
		requests \
		scipy \
		pydot \
		pandas \
		Sphinx \
		furo \
		scanpy \
		mygene \
		ipykernel \
		leidenalg \
		umap-learn==0.5.1 \
		--upgrade



.PHONY: freeze
freeze: ## Freeze package dependencies
	@$(PIP_OPT) freeze --exclude keggtools > requirements.txt



.PHONY: twine
twine: ## Twine package upload and checks
# Remove old keggtools package
	@$(PIP_OPT) uninstall $(PACKAGE_NAME) -y --quiet

# Remove dist folder
	@rm -rf ./dist/*

# Build package with flit backend
	@$(FLIT_OPT) build --setup-py

# Check package using twine
	@$(TWINE_OPT) check --strict ./dist/*

# Install package with flit
	@$(FLIT_OPT) install --deps=none



.PHONY : format
format: ## Lint and format code with flake8 and black
	@$(BLACK_OPT) $(PACKAGE_DIR) $(TEST_DIR) $(DOCS_DIR)/conf.py

	@$(FLAKE8_OPT) $(PACKAGE_DIR) $(TEST_DIR) $(DOCS_DIR)/conf.py


.PHONY: pytest
pytest: ## Unittest of package
	@$(TEST_OPT) --show-capture=log


.PHONY: mypy
mypy: ## Run static code analysis
	@$(MYPY_OPT) $(PACKAGE_DIR) $(TEST_DIR) $(DOCS_DIR)/conf.py



.PHONY: clean
clean: ## Clean all build and caching directories

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


	@$(SPHINX_OPT) -M doctest $(DOCS_DIR) $(DOCS_DIR)/_build
	@$(SPHINX_OPT) -M coverage $(DOCS_DIR) $(DOCS_DIR)/_build

# TODO: add latex pdf version of docs and copy to static files to include in HTML version
#	@$(SPHINX_OPT) -M latexpdf ./docs ./docs/_build && cp ./docs/_build/latex/keggtools.pdf ./docs/static/keggtools.pdf


# Build HTML version
	@$(SPHINX_OPT) -M html $(DOCS_DIR) $(DOCS_DIR)/_build





# Run all checks (always before committing!)
.PHONY: check
check: install freeze format mypy coverage twine docs precommit ## Full check of package




.PHONY : coverage
coverage: ## Run Coverage
	@$(COVERAGE_OPT) run -m pytest
	@$(COVERAGE_OPT) html --directory $(BASE_DIR)/coverage

# Long coverage report
	@$(COVERAGE_OPT) report -m



.PHONY : precommit
precommit: ## Run precommit file
#	@pre-commit run --all-files --verbose
	@pre-commit run --all-files


.PHONY : pdf
pdf: ## Generate Pdf file from latex

	cd ./reproducibility/latex; \
	biber paper; \
	pdflatex paper.tex

