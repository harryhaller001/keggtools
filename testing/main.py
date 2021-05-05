
from keggtools.models import KEGGPathway
from keggtools.resolver import KEGGPathwayResolver
from keggtools.analysis import KEGGPathwayAnalysisResult, KEGGPathwayAnalysis
from keggtools.render import KEGGPathwayRenderer
from keggtools.storage import KEGGDataStorage


import pandas
import os
import csv
import logging

GENE_DATA = os.path.join(os.getcwd(), "testing_dataset.csv")

if not os.path.isfile(GENE_DATA):
    logging.error(f"File {GENE_DATA} not found!")
    exit(1)


def load_bulk_data(filename: str):
    """
    Load differential expression gene data from csv
    :return: pandas.DataFrame
    """
    with open(filename, newline='') as f:
        csv_reader = csv.reader(f)
        csv_headings = next(csv_reader)
        logging.debug(f"Loading gene data with header {csv_headings}")
    
    return pandas.read_csv(filename, header=None, names=csv_headings,
                           skiprows=1)


# Load gene data from file
gene_df = load_bulk_data(filename=GENE_DATA)



# separate down-regulated genes
gene_df = gene_df[gene_df["log2FoldChange"] > 0]
print(gene_df.head())


# run analysis
analysis = KEGGPathwayAnalysis(org="mmu")
result = analysis.run_analysis(gene_list=gene_id_list)

# Save enrichment data
OUT_FILE = os.path.join(os.getcwd(),"kegg_pathway_result_Ctrl_vs_NTN.tsv")

file = open(OUT_FILE, "w")
file.write(analysis.export())
file.close()

print(f"KEGG Pathway result saved at {OUT_FILE}!")


exit(0)
