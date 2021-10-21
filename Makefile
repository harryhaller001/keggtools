
# Declare global variables

PACKAGE_NAME	= keggtools

PYTHON_OPT		= python3
PIP_OPT			= $(PYTHON_OPT) -m pip
MYPY_OPT		= $(PYTHON_OPT) -m mypy
LINT_OPT		= $(PYTHON_OPT) -m pylint
TEST_OPT		= $(PYTHON_OPT) -m pytest
TWINE_OPT		= $(PYTHON_OPT) -m twine
BANDIT_OPT		= $(PYTHON_OPT) -m bandit
SPHINX_OPT		= $(PYTHON_OPT) -m sphinx


# Run help by default

.DEFAULT_GOAL := help


# Ignore all command with no target file

.PHONY: clean, bandit, mypy check-updates, unittest, lint, check, devfreeze, freeze, devinstall, install, help, twine, docs



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






twine: # Twine package upload and checks
	$(PYTHON_OPT) setup.py install
	$(PYTHON_OPT) setup.py sdist bdist_wheel
	$(TWINE_OPT) check ./dist/*


lint: ## Linting package
	$(LINT_OPT) keggtools
	$(LINT_OPT) ./setup.py
	$(LINT_OPT) ./test/*.py


unittest: ## Unittest of package
	$(MYPY_OPT) ./test/test_package.py
	$(LINT_OPT) ./test/test_package.py
	$(TEST_OPT) -p keggtools --show-capture=log


mypy: ## Run static code analysis
	$(MYPY_OPT) setup.py
	$(MYPY_OPT) ./test/test_package.py
	$(MYPY_OPT) ./docs/conf.py
	$(MYPY_OPT) -p keggtools


check-updates: ## Check for updates of python pacakges
	$(PIP_OPT) install mypy pylint pytest twine setuptools --upgrade
	$(PIP_OPT) install requests scipy pydot tqdm --upgrade



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



# TODO: fix all common vulnerabilies in package
bandit: ## Run bandit analysis to find common security issues in code
	$(BANDIT_OPT) -r ./keggtools
	$(BANDIT_OPT) -r ./test
	$(BANDIT_OPT) setup.py
	$(BANDIT_OPT) -r ./docs/*.py



docs:
	$(PIP_OPT) install Sphinx sphinx-rtd-theme --upgrade
	$(MYPY_OPT) ./docs/conf.py
	$(LINT_OPT) ./docs/conf.py
	$(SPHINX_OPT) ./docs ./docs/_build


# Run all checks (always before committing!)
check: clean check-updates freeze devfreeze mypy lint unittest twine docs ## Full check of package
