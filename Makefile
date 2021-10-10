
# Declare global variables

PACKAGE_NAME	= keggtools

PYTHON_OPT		= python3
PIP_OPT			= $(PYTHON_OPT) -m pip
MYPY_OPT		= $(PYTHON_OPT) -m mypy
LINT_OPT		= $(PYTHON_OPT) -m pylint
TEST_OPT		= $(PYTHON_OPT) -m pytest

# Run help by default

.DEFAULT_GOAL := help


.PHONY: help

help: ## This help.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)




# Dependency handling

install: ## install all python dependencies
	$(PIP_OPT) install -r requirements.txt
	$(PYTHON_OPT) setup.py install

devinstall: ## Install python dependencies for development
	$(PIP_OPT) install -r requirements-dev.txt


freeze: ## Freeze package dependencies
	$(PIP_OPT) freeze | grep -E "requests==|tqdm==|pydot==|scipy==" > requirements.txt


devfreeze: ## Freeze all dependencies for development
	$(PIP_OPT) freeze --exclude keggtools > requirements-dev.txt



# Twine package upload and checks

check: clean check-updates ## Full check of package
	$(MYPY_OPT) setup.py
	$(PYTHON_OPT) setup.py install
	$(MYPY_OPT) -p keggtools
	$(PYTHON_OPT) setup.py sdist bdist_wheel
	twine check ./dist/*


lint: ## Linting package
	$(LINT_OPT) keggtools


unittest: ## Unittest of package
	$(MYPY_OPT) ./test/test_package.py
	$(LINT_OPT) ./test/test_package.py
	$(TEST_OPT) -p keggtools --show-capture=log

mypy: ## Run static code analysis


check-updates: ## Check for updates of python pacakges
	$(PIP_OPT) install mypy pylint pytest twine setuptools --upgrade
	$(PIP_OPT) install requests scipy pydot tqdm --upgrade


.PHONY: clean

clean: ## Clean all build and caching directories

# Remove package build folders
	rm -rf ./build
	rm -rf ./dist
	rm -rf ./$(PACKAGE_NAME).egg-info

# Remove mypy and pytest caching folders
	rm -rf ./.mypy_cache
	rm -rf ./.pytest_cache

# Remove build folders for docs
	rm -rf ./docs/_build
	rm -rf ./docs/dist
	rm -rf ./docs/cloudflare-workers/node_modules
	@echo "All build and caching folders removed"
