.DEFAULT_GOAL := check


# Dependency handling

install:
	python3 -m pip install -r requirements.txt
	python setup.py install

devinstall:
	python3 -m pip install -r requirements-dev.txt

freeze:
	python3 -m pip freeze \
		--exclude keggtools \
		--exclude mygene \
		--exclude pytest \
		--exclude mypy \
		--exclude mypy-extension \
		--exclude pandas > requirements.txt

devfreeze:
	python3 -m pip freeze --exclude keggtools > requirements-dev.txt



# Twine package upload and checks

check:
	mypy setup.py
	python setup.py install
	mypy -p keggtools
	rm ./dist/*
	python3 setup.py sdist bdist_wheel
	twine check ./dist/*

upload: check
	twine upload --skip-existing ./dist/*


lint:
	pylint keggtools



# TODO: implement unit testing
test:
	pytest keggtools

