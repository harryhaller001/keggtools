""" KEGG Enrichment analysis core """

import logging
import csv
import os
from typing import List, Any, Union
from io import TextIOWrapper
import scipy.stats as stats
from .resolver import KEGGPathwayResolver
# from .models import KEGGPathway
# from .storage import KEGGDataStorage


# def get_all_pathways(org: str):
#     filename = "pathways_{ORG}.dump".format(ORG=org)
#     if KEGGDataStorage.exist(filename=filename):
#         return KEGGDataStorage.load_dump(filename=filename)
#     else:
#         resolve = KEGGPathwayResolver(org=org)
#         pathways = resolve.get_pathway_list()
#         KEGGDataStorage.save_dump(filename=filename, data=pathways)
#         return pathways


class KEGGPathwayAnalysisResult:
    """
    Results of KEGG pathway enrichment analysis
    """

    # pylint: disable=too-many-instance-attributes,too-many-arguments
    def __init__(self,
                 org: str,
                 pathway_id: str,
                 pathway_name: str,
                 found_genes: list,
                 pathway_genes: list):

        """
        Init Result of KEGG pathway enrichment analysis
        :param org: str
        :param pathway_id: str
        :param pathway_name: str
        :param found_genes: list
        :param pathway_genes: list
        """

        self.organism: str = org
        self.pathway_id = pathway_id
        self.pathway_name = pathway_name
        self.found_genes = found_genes
        self.study_count = len(found_genes)
        self.pathway_genes = pathway_genes
        self.pathway_genes_count = len(pathway_genes)
        self.pvalue: Union[float, None] = None

        # self.args = {
        #     "organism": org,
        #     "pathway_id": pathway_id,
        #     "pathway_name": pathway_name,
        #     "found_genes": found_genes,
        #     "study_count": len(found_genes),
        #     "pathway_genes": pathway_genes,
        #     "pathway_genes_count": len(pathway_genes),
        #     "pvalue": "",
        # }


    def __str__(self):
        """
        Build string summary
        :return: str
        """
        return f"<KEGGPathwayAnalysisResult {self.organism}:{self.pathway_id}" \
                f" ({self.pathway_name}) {len(self.found_genes)}/{self.pathway_genes_count}>"


    def __repr__(self):
        """
        Print out string summary
        """
        return self.__str__()


    def set_pvalue(self, pval: float):
        """
        Set p value for enrichment analysis
        :param pval: float
        """
        # self.args["pvalue"] = pval
        self.pvalue = pval


    def json_summary(self, gene_delimiter=","):
        """
        Build json summary for enrichment analysis
        :param gene_delimiter: str
        :return: dict
        """

        # result = list()
        # result.append(self.args["pathway_name"])
        # result.append(self.args["pathway_id"])
        # result.append(str(len(self.args["found_genes"])))
        # result.append(str(len(self.args["pathway_genes"])))
        # result.append(str(self.args["pvalue"]))
        # result.append(",".join([str(a) for a in self.args["found_genes"]]))
        # # result.append(",".join([str(a) for a in self.args["pathway_genes"]]))
        # return "\t".join(result)

        result = {
            "pathway_name": self.pathway_name,
            "pathway_id": self.pathway_id,
            "study_count": self.study_count,
            "pathway_genes": self.pathway_genes_count,
            "pvalue": self.pvalue,
            "found_genes": gene_delimiter.join([str(a) for a in self.found_genes])
        }

        return result

    @staticmethod
    def get_header():
        """
        Build default header for enrichment analysis
        :return: list
        """

        # return list(self.args.keys())
        return ["pathway_name",
                "pathway_id",
                "study_count",
                "pathway_genes",
                "pvalue",
                "found_genes"]




class KEGGPathwayAnalysis:
    """
    KEGG pathway enrichment analysis
    """

    def __init__(self, org: str, pathways: Any = None):
        """
        Init KEGG pathway enrichment analysis
        :param org: str
        :param pathways: Any
        """

        self.organism = org
        self.summary: List[Any] = []
        self.resolver = KEGGPathwayResolver(self.organism)

        # self.all_pathways = get_all_pathways(org=self.organism)
        self.all_pathways = {}

        if pathways is None:
            # If pathways are not set use all pathways
            self.all_pathways = self.resolver.get_pathway_list()

        elif isinstance(pathways, dict):
            # Use given data when dict is passed
            self.all_pathways = pathways

        elif isinstance(pathways, list):
            # Load all pathways and filter for pathways in list
            for key, value in self.resolver.get_pathway_list().items():
                if key in pathways:
                    self.all_pathways[key] = value
            if len(self.all_pathways.keys()) == 0:
                raise ValueError("Pathways filter does not succeed. Still 0 pathways in list.")

        else:
            # still not pathways, raise error
            raise ValueError("Pass list or dict of pathways to filter list.")


    def _check_analysis_result_exist(self):
        """
        Check if summary exists
        :return: bool
        """
        if not self.summary or len(self.summary) == 0:
            raise ValueError("need to 'run_summary' first")


    def get_subset(self, subset: list, inplace=False):
        """
        Create subset of analysis result by list of pathway ids
        :param subset: list
        :param inplace: bool
        """
        self._check_analysis_result_exist()

        buffer = []
        subset = [str(s) for s in subset]
        for item in self.summary:
            if str(item.pathway_id) in subset:
                buffer.append(item)

        if inplace:
            self.summary = buffer

        return buffer


    def run_analysis(self, gene_list: list):
        """
        List of gene ids. Return list of KEGGPathwayAnalysisResult instances
        :param gene_list: list
        :return: list(KEGGPathwayAnalysisResult)
        """
        # pylint: disable=too-many-locals

        result = []
        all_found_genes = 0
        absolute_pathway_genes = 0
        study_n = len(gene_list)

        for pathway_id, name in self.all_pathways.items():

            pathway = self.resolver.get_pathway(code=pathway_id)
            # pathway = KEGGPathway.parse(KEGGDataStorage.load_pathway("mmu", pathway_id))

            genes_found = []
            all_pathways_genes = pathway.get_genes().keys()
            absolute_pathway_genes += len(all_pathways_genes)

            for gene_id in all_pathways_genes:
                if gene_id in gene_list:
                    genes_found.append(gene_id)

            all_found_genes += len(genes_found)
            pathway_result = KEGGPathwayAnalysisResult(org="mmu",
                                                       pathway_id=pathway_id,
                                                       pathway_name=name,
                                                       found_genes=genes_found,
                                                       pathway_genes=all_pathways_genes)
            result.append(pathway_result)

        # Perform Fisher exact test
        # http://docs.scipy.org/doc/scipy-0.17.0/reference/generated/scipy.stats.fisher_exact.html
        for analysis in result:

            # Skip p value calculation if no genes are found
            if analysis.study_count > 0:

                a_var = analysis.study_count
                b_var = study_n - analysis.study_count
                c_var = analysis.pathway_genes_count - analysis.study_count
                d_var = absolute_pathway_genes - analysis.pathway_genes_count - b_var

                # print(a_var, b_var, "\n", c_var, d_var,
                # "\n" + str(absolute_pathway_genes) + "-" * 10)

                _, pval = stats.fisher_exact(
                    [
                        [
                            a_var,
                            b_var
                        ],
                        [
                            c_var,
                            d_var
                        ]
                    ]
                )

                analysis.set_pvalue(pval=pval)
            else:
                logging.debug("No genes found for %s:%s." \
                              " p value calculation skipped.",
                              analysis.organism,
                              analysis.pathway_id)

        self.summary = result
        return result


    # def export(self):

    #     # Check if summary exists
    #     if not self.summary:
    #         raise ValueError("need to 'run_summary' first")

    #     result = list()
    #     result.append("\t".join(KEGGPathwayAnalysisResult.get_header()))

    #     # export as file option
    #     # use csv dict writer

    #     for item in self.summary:
    #         result.append(item.line_summary())
    #     return "\n".join(result)


    def to_dataframe(self):
        """
        Return analysis result as pandas DataFrame
        """
        try:
            # Ignore import lint at this place to keep pandas an optional dependency
            # pylint: disable=import-outside-toplevel
            import pandas

            # Check if summary exists
            self._check_analysis_result_exist()
            summary_list = []
            for result in self.summary:
                summary_list.append(result.json_summary())
            return pandas.DataFrame(summary_list)
        except ImportError:
            logging.error("Package 'pandas' is not installed." \
                          "To use this function please 'pip install pandas'")
            return None


    def fexport(self, file: Union[str, TextIOWrapper], delimiter="\t", overwrite=False):
        """
        Save result summary as file
        :param file: Union[str, TextIOWrapper]
        :param delimiter: str
        :param overwrite: bool
        """

        # Check if summary exists
        self._check_analysis_result_exist()

        if isinstance(file, str):
            # file is str (Name of file)
            if os.path.isfile(file) and not overwrite:
                raise RuntimeError(f"File {file} does already exist." \
                                    "To solve please set overwrite=True.")

            csv_file = open(file, mode="w", encoding="utf-8")
        elif isinstance(file, TextIOWrapper):
            # file is TextIOWrapper (File object stream)
            csv_file = file


        # Delimiter of gene names
        child_delimiter = ","

        # Change child delimiter to aviod csv conficts
        if delimiter == child_delimiter:
            child_delimiter = ";"

        headers: List[str] = KEGGPathwayAnalysisResult.get_header()
        writer = csv.DictWriter(csv_file, fieldnames=headers)

        for item in self.summary:
            # Write lines
            writer.writerow(item.json_summary(gene_delimiter=child_delimiter))

        csv_file.close()


if __name__ == "__main__":
    pass
