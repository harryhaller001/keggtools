
# Declare global variables

BASE_DIR		= ${PWD}

PACKAGE_NAME	= keggtools

PACKAGE_DIR		= $(BASE_DIR)/src/keggtools
TEST_DIR		= $(BASE_DIR)/tests
DOCS_DIR		= $(BASE_DIR)/docs

UV_OPT			= uv
UV_RUN_OPT		= $(UV_OPT) run
PYTHON_OPT		= $(UV_RUN_OPT) python
TY_OPT			= $(UV_RUN_OPT) ty
TEST_OPT		= $(UV_RUN_OPT) pytest
TWINE_OPT		= $(UV_RUN_OPT) twine
SPHINX_OPT		= $(PYTHON_OPT) -m sphinx
RUFF_OPT		= $(UV_RUN_OPT) ruff
PRE_COMMIT_OPT	= $(UV_RUN_OPT) pre-commit

# Run help by default

.DEFAULT_GOAL := help



.PHONY : help
help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)




# Dependency handling

.PHONY : install
install: ## install all python dependencies

# Install dev dependencies
	@$(UV_OPT) sync --all-extras

# Install precommit hook
	@$(PRE_COMMIT_OPT) install




.PHONY : build
build: # Twine package upload and checks

# Remove dist folder
	@rm -rf ./dist/*

	@$(UV_OPT) build

# Check package using twine
	@$(TWINE_OPT) check --strict ./dist/*




.PHONY : format
format: ## Lint and format code with flake8 and black
	@$(RUFF_OPT) format $(PACKAGE_DIR) $(TEST_DIR) $(DOCS_DIR)/conf.py
	@$(RUFF_OPT) check --fix $(PACKAGE_DIR) $(TEST_DIR) $(DOCS_DIR)/conf.py



.PHONY: testing
testing: ## Unittest of package
	@$(TEST_OPT)

.PHONY: typing
typing: ## Run static code analysis
	@$(TY_OPT) check $(PACKAGE_DIR) $(TEST_DIR) $(DOCS_DIR)/conf.py



.PHONY: clean
clean: ## Clean all build and caching directories

# Remove package build folders
	@rm -rf ./build
	@rm -rf ./dist
	@rm -rf ./$(PACKAGE_NAME).egg-info

# Remove ty and pytest caching folders
	@rm -rf ./.pytest_cache
	@rm -rf ./coverage
	@rm -f .coverage

# Remove build folders for docs
	@rm -rf ./docs/_build
	@rm -rf ./docs/dist



.PHONY: docs
docs: ## Build sphinx docs
	@rm -rf ./docs/_build

	@$(SPHINX_OPT) -M doctest $(DOCS_DIR) $(DOCS_DIR)/_build
	@$(SPHINX_OPT) -M coverage $(DOCS_DIR) $(DOCS_DIR)/_build

# Build HTML version
	@$(SPHINX_OPT) -M html $(DOCS_DIR) $(DOCS_DIR)/_build





# Run all checks (always before committing!)
.PHONY: check
check: install format typing testing build docs precommit ## Full check of package



.PHONY : precommit
precommit: ## Run precommit file
#	@pre-commit run --all-files --verbose
	@$(PRE_COMMIT_OPT) run --all-files


.PHONY : open-docs
open-docs: ## Open build docs in webbrowser
	@$(PYTHON_OPT) -m webbrowser -t file:///${PWD}/docs/_build/html/index.html
