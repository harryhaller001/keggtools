
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

# Run help by default

.DEFAULT_GOAL := help


.PHONY: help
help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)




# Dependency handling

.PHONY: install
install: ## install all python dependencies
	@$(PIP_OPT) install mypy pylint pytest coverage twine setuptools types-requests responses --upgrade
	@$(PIP_OPT) install requests scipy pydot pandas --upgrade
	@$(PIP_OPT) install Sphinx sphinx-rtd-theme --upgrade
	@$(PYTHON_OPT) setup.py install


.PHONY: freeze
freeze: ## Freeze package dependencies
	@$(PIP_OPT) freeze | grep -E "^requests==|pydot==|scipy==" > requirements.txt
	@$(PIP_OPT) freeze --exclude keggtools > requirements-dev.txt


# .PHONY: devfreeze
# devfreeze: ## Freeze all dependencies for development
# 	$(PIP_OPT) freeze --exclude keggtools > requirements-dev.txt





.PHONY: twine
twine: ## Twine package upload and checks
	@$(PYTHON_OPT) setup.py install
	@$(PYTHON_OPT) setup.py sdist bdist_wheel
	@$(TWINE_OPT) check --strict ./dist/*

# TODO: remove legacy build and switch to build
# python -m build --sdist --wheel


.PHONY: pylint
pylint: ## Linting package
	@$(LINT_OPT) keggtools
	@$(LINT_OPT) ./setup.py
	@$(LINT_OPT) ./test/*.py
	@$(LINT_OPT) ./docs/conf.py

.PHONY: pytest
pytest: ## Unittest of package
	@$(TEST_OPT) -p keggtools --show-capture=log


.PHONY: mypy
mypy: ## Run static code analysis
	@$(MYPY_OPT) setup.py
	@$(MYPY_OPT) ./test
	@$(MYPY_OPT) ./docs/conf.py
	@$(MYPY_OPT) -p keggtools




.PHONY: clean
clean: ## Clean all build and caching directories

# Remove old keggtools package
	pip uninstall keggtools -y --quiet

# Remove package build folders
	rm -rf ./build
	rm -rf ./dist
	rm -rf ./$(PACKAGE_NAME).egg-info

# Remove mypy and pytest caching folders
	rm -rf ./.mypy_cache
	rm -rf ./.pytest_cache
	rm -rf ./coverage
	rm -f .coverage

# Remove build folders for docs
	rm -rf ./docs/_build
	rm -rf ./docs/dist
	rm -rf ./docs/cloudflare-workers/node_modules
	@echo "All build and caching folders removed"




.PHONY: docs
docs: ## Build sphinx docs
	@rm -rf ./docs/_build
	@$(SPHINX_OPT) -M html ./docs ./docs/_build
	@$(SPHINX_OPT) -M coverage ./docs ./docs/_build

# TODO: add latex pdf version of docs
#	@$(SPHINX_OPT) -M latexpdf ./docs ./docs/_build


# Run all checks (always before committing!)
.PHONY: check
check: clean freeze pylint mypy coverage twine docs ## Full check of package




.PHONY : coverage
coverage: ## Run Coverage
	@$(COVERAGE_OPT) run -m pytest
	@$(COVERAGE_OPT) html --directory $(BASE_DIR)/coverage

# Long coverage report
	@$(COVERAGE_OPT) report -m

