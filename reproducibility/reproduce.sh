#!/bin/bash

BASEDIR=${PWD}

# Figure 1
dot ${BASEDIR}/figures/figure1.dot -Tpng -Gdpi=300 > ${BASEDIR}/figures/figure1.png


# Compile latex file to pdf
cd ${BASEDIR}/latex && pdflatex paper.tex

