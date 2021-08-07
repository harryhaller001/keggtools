.DEFAULT_GOAL := check


# Dependency handling

install:
	python3 -m pip install -r requirements.txt
	python setup.py install

devinstall:
	python3 -m pip install -r requirements-dev.txt

freeze:
# python3 -m pip freeze \
# 	--exclude keggtools \
# 	--exclude mygene \
# 	--exclude pytest \
# 	--exclude mypy \
# 	--exclude mypy-extension \
# 	--exclude pandas > requirements.txt
	@pip freeze | grep -E "requests==|tqdm==|pydot==|scipy==" > requirements.txt

devfreeze:
	python3 -m pip freeze --exclude keggtools > requirements-dev.txt



# Twine package upload and checks

check: check-updates
	mypy setup.py
	python setup.py install
	mypy -p keggtools
	rm ./dist/*
	python3 setup.py sdist bdist_wheel
	twine check ./dist/*


# upload: check
# 	twine upload --skip-existing ./dist/*


lint: check-updates
	pylint keggtools



# run unit testing

unittest: check-updates
	@mypy ./test/test_package.py
	@pylint ./test/test_package.py
	@pytest -p keggtools --show-capture=log


check-updates:
	python -m pip install mypy pylint pytest twine setuptools --upgrade
	python -m pip install requests scipy pydot tqdm --upgrade

# Dev freeze
	python3 -m pip freeze --exclude keggtools > requirements-dev.txt
