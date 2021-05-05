
from .models import KEGGPathway
from .storage import KEGGDataStorage
from .resolver import KEGGPathwayResolver
from typing import List, Any
import scipy.stats as stats


def get_all_pathways(org: str):
    filename = "pathways_{ORG}.dump".format(ORG=org)
    if KEGGDataStorage.exist(filename=filename):
        return KEGGDataStorage.load_dump(filename=filename)
    else:
        resolve = KEGGPathwayResolver(org=org)
        pathways = resolve.get_pathway_list()
        KEGGDataStorage.save_dump(filename=filename, data=pathways)
        return pathways


"""
TODO: p-value calculation
"""


class KEGGPathwayAnalysisResult:
    def __init__(self, org: str, pathway_id: str, pathway_name: str, found_genes: list, pathway_genes: list):
        self.args = {
            "organism": org,
            "pathway_id": pathway_id,
            "pathway_name": pathway_name,
            "found_genes": found_genes,
            "study_count": len(found_genes),
            "pathway_genes": pathway_genes,
            "pathway_genes_count": len(pathway_genes),
            "pvalue": "",
        }

    def set_pvalue(self, pval):
        self.args["pvalue"] = pval

    def __getattr__(self, item):
        return self.args.get(item, None)

    def line_summary(self):
        result = list()
        result.append(self.args["pathway_name"])
        result.append(self.args["pathway_id"])
        result.append(str(len(self.args["found_genes"])))
        result.append(str(len(self.args["pathway_genes"])))
        result.append(str(self.args["pvalue"]))
        result.append(",".join([str(a) for a in self.args["found_genes"]]))
        # result.append(",".join([str(a) for a in self.args["pathway_genes"]]))

        return "\t".join(result)

    @staticmethod
    def get_header():
        return "\t".join(["pathway_name", "pathway_id", "study_count", "pathway_genes", "pvalue", "found_genes"])




class KEGGPathwayAnalysis:
    def __init__(self, org: str):
        self.organism = org
        self.summary: List[Any] = []
        self.all_pathways = get_all_pathways(org=self.organism)

    def sort_subset(self, subset: list):
        buffer = []
        subset = [str(s) for s in subset]
        for item in self.summary:
            if str(item.pathway_id) in subset:
                buffer.append(item)
        self.summary = buffer

    """def run_analysis(self, gene_list: list):
        
        # List of gene ids. Return {<pathway-id>: [<gene-id>, ...]}
        # :param gene_list: list
        # :return: dict
        
        result = {}

        for pathway_id, name in self.all_pathways.items():
            pathway = KEGGPathway.parse(KEGGDataStorage.load_pathway("mmu", pathway_id))

            genes_found = []
            for gene_id in pathway.get_genes().keys():
                if gene_id in gene_list:
                    genes_found.append(gene_id)
            result[pathway_id] = genes_found
        self.summary = result
        return result"""

    def run_analysis(self, gene_list: list):
        """
        List of gene ids. Return {<pathway-id>: [<gene-id>, ...]}
        :param gene_list: list
        :return: list(KEGGPathwayAnalysisResult)
        """
        result = []

        all_found_genes = 0
        absolute_pathway_genes = 0

        for pathway_id, name in self.all_pathways.items():
            pathway = KEGGPathway.parse(KEGGDataStorage.load_pathway("mmu", pathway_id))

            genes_found = []
            all_pathways_genes = pathway.get_genes().keys()
            absolute_pathway_genes += len(all_pathways_genes)

            for gene_id in all_pathways_genes:
                if gene_id in gene_list:
                    genes_found.append(gene_id)

            all_found_genes += len(genes_found)
            pathway_result = KEGGPathwayAnalysisResult(org="mmu", pathway_id=pathway_id, pathway_name=name, found_genes=genes_found, pathway_genes=all_pathways_genes)
            result.append(pathway_result)

        # Perform Fisher exact test

        for analysis in result:
            _, pval = stats.fisher_exact(
                [[analysis.study_count,
                  all_found_genes - analysis.study_count],

                 [analysis.pathway_genes_count - analysis.study_count,
                  absolute_pathway_genes - analysis.pathway_genes_count]]
            )
            analysis.set_pvalue(pval=pval)

        self.summary = result
        return result

    def export(self):
        if not self.summary:
            raise ValueError("need to 'run_summary' first")

        result = list()
        result.append(KEGGPathwayAnalysisResult.get_header())

        """for pathway_id, gene_list in self.summary.items():
            gene_symbols = []
            for gene_id in gene_list:
                gene_symbols.append(self.converter.geneid_to_symbol(gene_id))
            result.append("{PATHWAY}\t{PATHWAY_ID}\t{COUNT}\t{GENES}".
                          format(PATHWAY=self.all_pathways.get(pathway_id, ""),
                                 PATHWAY_ID=pathway_id, COUNT=len(gene_symbols),
                                 GENES=",".join(gene_symbols)))
        """
        for item in self.summary:
            result.append(item.line_summary())
        return "\n".join(result)


if __name__ == "__main__":
    pass

