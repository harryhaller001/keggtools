
import logging
logging.basicConfig(level=logging.DEBUG)

import os
os.environ["KEGG_DATA"] = os.path.join(os.getcwd(), ".cache")

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
cluster = 4
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

# print(analysis.all_pathways)

# TODO: load and parse all pathways

# analysis.run_analysis(gene_list=gene_list)
# resolver = KEGGPathwayResolver(organism_id)
# print(resolver.get_pathway_list())

pathway_id = list(IMMUNE_SYSTEM_PATHWAYS.keys())[1]

print(pathway_id, IMMUNE_SYSTEM_PATHWAYS[pathway_id])

resolver = KEGGPathwayResolver(organism_id)
pathway = resolver.get_pathway(code=pathway_id)

print(pathway)

print(list(pathway.get_genes().keys()))

# Convert to list of entez ids using mygene
# gene_list
import mygene
mg = mygene.MyGeneInfo()

print(gene_list)

query_result = mg.querymany(gene_list, scopes="symbol", species="human")
# print(query_result)

entrz_gene_list= [] # = [q["entrezgene"] for q in query_result]
for item in query_result:
    # print(item)
    if "entrezgene" in item:
        entrz_gene_list.append(int(item["entrezgene"]))
    else:
        print(f"Not found entrz in", item)

print(entrz_gene_list)

analysis.run_analysis(gene_list=entrz_gene_list)

import os
export_filename = os.path.join(os.getcwd(), "test.tsv")

# Export analysis result
analysis.fexport(file=export_filename, overwrite=True)

for analysis_result in analysis.summary:
    print(analysis_result.pathway_name, analysis_result.pvalue, analysis_result.study_count, analysis_result.pathway_genes_count)

result_df = analysis.to_dataframe()

print(result_df)

import matplotlib.pyplot as plt
import math

plt.figure(figsize=(8, 5), dpi=300)
scatter = plt.scatter(x=result_df["study_count"], y=result_df["pathway_name"], c=[-math.log10(x) for x in result_df["pvalue"]], cmap="coolwarm")
cbar = plt.colorbar()
cbar.set_label("- log10(p value)")

plt.tight_layout()
plt.savefig("test.png", bbox_inches='tight')

if __name__ == "__main__":
    pass

