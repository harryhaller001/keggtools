
install:
	python3 -m pip install -r requirements.txt

devinstall:
	python3 -m pip install -r requirements-dev.txt

freeze:
	python3 -m pip freeze \
		--exclude keggtools \
		--exclude pytest \
		--exclude mypy \
		--exclude mypy-extension \
		--exclude pandas > requirements.txt

devfreeze:
	python3 -m pip freeze --exclude keggtools > requirements-dev.txt


