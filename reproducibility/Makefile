


.PHONY : figures
figures: ## Generate figures

# Generate figures from dot
	dot ./figures/figure1.dot -Tpng -Gdpi=300 > ./figures/figure1.png
	dot ./figures/figure5.dot -Tpng -Gdpi=300 > ./figures/figure5.png



pdf: figures ## Generate Pdf file from latex

	cd ./latex; \
	biber paper; \
	pdflatex paper.tex

