
# Declare global variables

BASE_DIR		= ${PWD}

PACKAGE_NAME	= keggtools

PACKAGE_DIR		= $(BASE_DIR)/keggtools
TEST_DIR		= $(BASE_DIR)/tests
DOCS_DIR		= $(BASE_DIR)/docs

PYTHON_OPT		= python3
PIP_OPT			= $(PYTHON_OPT) -m pip --require-virtualenv
MYPY_OPT		= $(PYTHON_OPT) -m mypy
TEST_OPT		= $(PYTHON_OPT) -m pytest
TWINE_OPT		= $(PYTHON_OPT) -m twine
SPHINX_OPT		= $(PYTHON_OPT) -m sphinx
COVERAGE_OPT	= $(PYTHON_OPT) -m coverage
FLIT_OPT		= $(PYTHON_OPT) -m flit
RUFF_OPT		= $(PYTHON_OPT) -m ruff
PRE_COMMIT_OPT	= pre-commit

# Run help by default

.DEFAULT_GOAL := help



.PHONY : help
help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)




# Dependency handling

.PHONY : install
install: ## install all python dependencies

# Install dev dependencies
	@$(PIP_OPT) install -e ".[test,docs]" --upgrade

# Install precommit hook
	@$(PRE_COMMIT_OPT) install

.PHONY : freeze
freeze: ## Freeze package dependencies
	@$(PYTHON_OPT) --version > .python-version
	@$(PIP_OPT) freeze --exclude $(PACKAGE_NAME) > requirements.txt




.PHONY : build
build: # Twine package upload and checks

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
	@$(RUFF_OPT) format $(PACKAGE_DIR) $(TEST_DIR) $(DOCS_DIR)/source/conf.py
	@$(RUFF_OPT) check --fix $(PACKAGE_DIR) $(TEST_DIR) $(DOCS_DIR)/source/conf.py


.PHONY: testing
testing: ## Unittest of package
# @$(TEST_OPT) --show-capture=log

	@$(COVERAGE_OPT) run -m pytest
	@$(COVERAGE_OPT) html

# Long coverage report
	@$(COVERAGE_OPT) report -m


.PHONY: typing
typing: ## Run static code analysis
	@$(MYPY_OPT) $(PACKAGE_DIR) $(TEST_DIR) $(DOCS_DIR)/source/conf.py



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
	@rm -rf .pybiomart.sqlite

# Remove build folders for docs
	@rm -rf ./docs/_build
	@rm -rf ./docs/.keggtools_cache
	@rm -rf ./docs/.pybiomart.sqlite



.PHONY: docs
docs: ## Build sphinx docs
	@rm -rf ./docs/_build

# Generate dot graphics
	dot ./docs/source/figures/figure1.dot -Tpng -Gdpi=300 > ./docs/source/figures/figure1.png
	dot ./docs/source/figures/figure5.dot -Tpng -Gdpi=300 > ./docs/source/figures/figure5.png

	@$(SPHINX_OPT) -M doctest $(DOCS_DIR)/source $(DOCS_DIR)/_build
	@$(SPHINX_OPT) -M coverage $(DOCS_DIR)/source $(DOCS_DIR)/_build

# Build HTML version
	@$(SPHINX_OPT) -M html $(DOCS_DIR)/source $(DOCS_DIR)/_build





# Run all checks (always before committing!)
.PHONY: check
check: install freeze format typing testing build docs precommit ## Full check of package



.PHONY : precommit
precommit: ## Run precommit file
#	@pre-commit run --all-files --verbose
	@$(PRE_COMMIT_OPT) run --all-files


.PHONY : open-docs
open-docs: ## Open build docs in webbrowser
	@$(PYTHON_OPT) -m webbrowser -t file:///${PWD}/docs/_build/html/index.html
