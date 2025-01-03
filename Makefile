
# Declare global variables

PACKAGE_NAME	= keggtools

BASE_DIR		= ${PWD}

PACKAGE_DIR		= $(BASE_DIR)/$(PACKAGE_NAME)
TEST_DIR		= $(BASE_DIR)/test
DOCS_DIR		= $(BASE_DIR)/docs


PYTHON_OPT		= python3
PIP_OPT			= $(PYTHON_OPT) -m pip --require-virtualenv
MYPY_OPT		= $(PYTHON_OPT) -m mypy
TEST_OPT		= $(PYTHON_OPT) -m pytest
TWINE_OPT		= $(PYTHON_OPT) -m twine
SPHINX_OPT		= $(PYTHON_OPT) -m sphinx
COVERAGE_OPT	= $(PYTHON_OPT) -m coverage
FLIT_OPT		= $(PYTHON_OPT) -m flit
PRECOMMIT_OPT	= pre-commit
RUFF_OPT		= $(PYTHON_OPT) -m ruff

# Run help by default

.DEFAULT_GOAL := help


.PHONY: help
help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)




# Dependency handling

.PHONY: install
install: ## install all python dependencies
	@$(PIP_OPT) install ".[test,docs]" --upgrade

	@$(PRECOMMIT_OPT) install


.PHONY: freeze
freeze: ## Freeze package dependencies
	@$(PIP_OPT) freeze --exclude keggtools > requirements.txt
	@$(PYTHON_OPT) --version > .python-version


.PHONY: build
build: ## Build package upload and checks
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
format: ## Lint and format code

	@$(RUFF_OPT) format keggtools/*.py
	@$(RUFF_OPT) check --fix keggtools/*.py

	@$(RUFF_OPT) format test/*.py
	@$(RUFF_OPT) check --fix test/*.py


.PHONY: unittest
unittest: ## Unittest of package
	@$(TEST_OPT) --show-capture=log


.PHONY: typing
typing: ## Run static code analysis
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
	dot ./docs/figures/figure1.dot -Tpng -Gdpi=300 > ./docs/figures/figure1.png
	dot ./docs/figures/figure5.dot -Tpng -Gdpi=300 > ./docs/figures/figure5.png


	@$(SPHINX_OPT) -M doctest $(DOCS_DIR) $(DOCS_DIR)/_build
	@$(SPHINX_OPT) -M coverage $(DOCS_DIR) $(DOCS_DIR)/_build

# TODO: add latex pdf version of docs and copy to static files to include in HTML version
#	@$(SPHINX_OPT) -M latexpdf ./docs ./docs/_build && cp ./docs/_build/latex/keggtools.pdf ./docs/static/keggtools.pdf


# Build HTML version
	@$(SPHINX_OPT) -M html $(DOCS_DIR) $(DOCS_DIR)/_build





# Run all checks (always before committing!)
.PHONY: check
check: install freeze format typing coverage build docs precommit ## Full check of package




.PHONY : coverage
coverage: ## Run Coverage
	@$(COVERAGE_OPT) run -m pytest
	@$(COVERAGE_OPT) html --directory $(BASE_DIR)/coverage

# Long coverage report
	@$(COVERAGE_OPT) report -m



.PHONY : precommit
precommit: ## Run precommit file
#	@pre-commit run --all-files --verbose
	@$(PRECOMMIT_OPT) run --all-files


# .PHONY : pdf
# pdf: ## Generate Pdf file from latex
# 	cd ./reproducibility/latex; \
# 	biber paper; \
# 	pdflatex paper.tex

