
# Declare global variables

BASE_DIR		= ${PWD}

PACKAGE_NAME	= keggtools

PACKAGE_DIR		= $(BASE_DIR)/keggtools
TEST_DIR		= $(BASE_DIR)/tests
DOCS_DIR		= $(BASE_DIR)/docs

UV_OPT			= uv run
MYPY_OPT		= $(UV_OPT) mypy
TEST_OPT		= $(UV_OPT) pytest
TWINE_OPT		= $(UV_OPT) twine
SPHINX_OPT		= $(UV_OPT) python -m sphinx
COVERAGE_OPT	= $(UV_OPT) coverage
FLIT_OPT		= $(UV_OPT) flit
RUFF_OPT		= $(UV_OPT) ruff
PRE_COMMIT_OPT	= $(UV_OPT) pre-commit

# Run help by default

.DEFAULT_GOAL := help



.PHONY : help
help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)




# Dependency handling

.PHONY : install
install: ## install all python dependencies

# Install dev dependencies
	uv sync --all-extras

# Install pre-commit hooks
	@$(PRE_COMMIT_OPT) install



.PHONY : build
build: # Twine package upload and checks

# Remove dist folder
	@rm -rf ./dist/*

	uv build

# Check package using twine
	@$(TWINE_OPT) check --strict ./dist/*



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
check: install format typing testing build docs precommit ## Full check of package



.PHONY : precommit
precommit: ## Run precommit file
#	@pre-commit run --all-files --verbose
	@$(PRE_COMMIT_OPT) run --all-files


.PHONY : open-docs
open-docs: ## Open build docs in webbrowser
	@$(UV_OPT) python -m webbrowser -t file:///${PWD}/docs/_build/html/index.html
