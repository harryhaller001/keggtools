#!/bin/bash

# Download PBMC3K
curl https://cf.10xgenomics.com/samples/cell/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz -o ${PWD}/pbmc3k.tar.gz

# Decompress folder
tar -zvxf ${PWD}/pbmc3k.tar.gz --directory ${PWD}/notebooks/rawdata --strip=2
