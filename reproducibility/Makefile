build:
	docker-compose -f docker-compose.yml build --no-cache

down:
	docker-compose -f docker-compose.yml down

start:
	docker-compose -f docker-compose.yml up


pdf:
	cd ./latex; \
	biber paper; \
	pdflatex paper.tex

