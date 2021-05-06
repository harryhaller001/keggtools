
import logging
logging.basicConfig(level=logging.DEBUG)

import pandas
import csv
from keggtools.models import KEGGPathway
from keggtools.resolver import KEGGPathwayResolver
from keggtools.analysis import KEGGPathwayAnalysisResult, KEGGPathwayAnalysis
from keggtools.render import KEGGPathwayRenderer
from keggtools.storage import KEGGDataStorage

from keggtools.const import IMMUNE_SYSTEM_PATHWAYS

# Get all components
# components = KEGGPathwayResolver.get_components()

# # List all pathways
# organism_id = "hsa"

# # Resolve list of pathways
# resolver = KEGGPathwayResolver(organism_id)
# all_pathways = resolver.get_pathway_list()

# print(len(all_pathways))

# loaded_pathways = []

# # Check if organism has all immune system pathways
# for immune_pathway in IMMUNE_SYSTEM_PATHWAYS:
#     if not immune_pathway in all_pathways.keys():
#         raise ValueError(f"pathway {immune_pathway} not found.")

#     else:
#         # Load and parse all immune system pathways
#         loaded_pathways.append()

# Load differential expression data

organism_id = "hsa"
filename = "./export_uns.csv"
cluster = 0
with open(filename, newline='') as f:
    csv_reader = csv.reader(f)
    csv_headings = next(csv_reader)
    # logging.debug(f"Loading gene data with header {csv_headings}")

analysis =  pandas.read_csv(filename, header=None, names=csv_headings, skiprows=1)

# Filter for cluster
analysis = analysis[analysis["cluster"] == cluster]
print(analysis.head())

# Get genes as list
gene_list = list(analysis["names"])
print(len(gene_list), "genes in list")


analysis = KEGGPathwayAnalysis(org=organism_id, pathways=IMMUNE_SYSTEM_PATHWAYS)
# analysis.run_analysis(gene_list=gene_list)
# resolver = KEGGPathwayResolver(organism_id)
# print(resolver.get_pathway_list())
print(analysis.all_pathways)



if __name__ == "__main__":
    pass

