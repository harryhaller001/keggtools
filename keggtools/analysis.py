"""KEGG Enrichment analysis core."""

import math
import os
from csv import DictWriter
from io import IOBase
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from scipy import stats

from .models import Pathway


class EnrichmentResult:
    """Results of KEGG pathway enrichment analysis."""

    def __init__(
        self,
        org: str,
        pathway_id: str,
        pathway_name: str,
        found_genes: list,
        pathway_genes: list,
        pathway_title: str | None = None,
    ) -> None:
        """Init Result of KEGG pathway enrichment analysis.

        :param str org: 3 letter code of organism used by KEGG database.
        :param str pathway_id: Identifier of KEGG pathway.
        :param str pathway_name: Name of KEGG pathway.
        :param list found_genes: List of found genes.
        :param list pathway_genes: List of all genes in pathway.
        """
        # Pathway descriptions
        self.organism: str = org
        self.pathway_id: str = pathway_id
        self.pathway_name: str = pathway_name
        self.pathway_title: str | None = pathway_title

        # Results from enrichment analysis
        self.found_genes: list = found_genes
        self.pathway_genes: list = pathway_genes
        self.pvalue: float | None = None

    @property
    def pathway_genes_count(self) -> int:
        """Count of pathway genes.

        :rtype: int
        :return: Number of genes in pathway.
        """
        return len(self.pathway_genes)

    @property
    def study_count(self) -> int:
        """Count of study genes.

        :rtype: int
        :return: Number of genes found in analysis of pathway.
        """
        return len(self.found_genes)

    def __str__(self) -> str:
        """Build string summary of KEGG path analysis result instance.

        :rtype: str
        :return: Returns string that describes the enrichment result instance.
        """
        return (
            f"<EnrichmentResult {self.organism}:{self.pathway_id}"
            f" ({self.pathway_name}) {len(self.found_genes)}/{self.pathway_genes_count}>"
        )

    def json_summary(self, gene_delimiter: str = ",") -> dict[str, Any]:
        """Build json summary for enrichment analysis.

        :param str gene_delimiter: Delimiter to seperate genes in gene list.
        :rtype: typing.Dict[str, typing.Any]
        :return: Summary of enrichment result instance as dict.
        """
        return {
            "pathway_name": self.pathway_name,
            "pathway_title": self.pathway_title,
            "pathway_id": self.pathway_id,
            "study_count": self.study_count,
            "pathway_genes": self.pathway_genes_count,
            "pvalue": self.pvalue,
            "found_genes": gene_delimiter.join([str(a) for a in self.found_genes]),
        }

    @staticmethod
    def get_header() -> list[str]:
        """Build default header for enrichment analysis.

        :rtype: typing.List[str]
        :return: List of header names as string.
        """
        return [
            "pathway_name",
            "pathway_title",
            "pathway_id",
            "study_count",
            "pathway_genes",
            "pvalue",
            "found_genes",
        ]


class Enrichment:
    """KEGG pathway enrichment analysis."""

    def __init__(
        self,
        pathways: list[Pathway],
    ) -> None:
        """Init KEGG pathway enrichment analysis.

        :param str org: Organism identifier used by KEGG database (3 letter code, e.g. "mmu" for mus musculus or "hsa" for human).
        :param typing.List[Pathway] pathways: (Optional) List of Pathway instances or list of KEGG pathway identifier.
        """
        self.result: list[EnrichmentResult] = []

        # Create pathway list
        self.all_pathways: list[Pathway] = pathways

    def _check_analysis_result_exist(self) -> None:
        """Check if summary exists."""
        if not self.result or len(self.result) == 0:
            raise ValueError("need to 'run_analysis' first")

    def get_subset(self, subset: list[str], inplace: bool = False) -> list[EnrichmentResult]:
        """Create subset of analysis result by list of pathway ids.

        :param typing.List[str] subset: List of pathway identifer to filter enrichment result by.
        :param bool inplace: Update instance variable of enrichment result list and overwrite with generated subset.
        :return: Subset of enrichment results.
        :rtype: typing.List[EnrichmentResult]
        """
        self._check_analysis_result_exist()

        buffer = []
        # subset = [str(s) for s in subset]
        for item in self.result:
            if str(item.pathway_id) in subset:
                buffer.append(item)

        if inplace is True:
            self.result = buffer

        return buffer

    def run_analysis(self, gene_list: list[str]) -> list[EnrichmentResult]:
        """List of gene ids. Return list of EnrichmentResult instances.

        :param typing.List[str] gene_list: List of genes to analyse.
        :return: List of enrichment result instances.
        :rtype: typing.List[EnrichmentResult]
        """
        all_found_genes: int = 0
        absolute_pathway_genes: int = 0
        study_n: int = len(gene_list)

        for pathway in self.all_pathways:
            genes_found: list[str] = []
            all_pathways_genes = pathway.get_genes()
            absolute_pathway_genes += len(all_pathways_genes)

            # Check for intersection between gene list and genes in pathway
            for gene_id in all_pathways_genes:
                if gene_id in gene_list:
                    genes_found.append(gene_id)

            all_found_genes += len(genes_found)

            # Create analysis results instance and append to list of results
            pathway_result: EnrichmentResult = EnrichmentResult(
                org=pathway.org,
                pathway_id=pathway.number,
                pathway_name=pathway.name,
                pathway_title=pathway.title,
                found_genes=genes_found,
                pathway_genes=all_pathways_genes,
            )
            self.result.append(pathway_result)

        # Perform Fisher exact test
        # http://docs.scipy.org/doc/scipy-0.17.0/reference/generated/scipy.stats.fisher_exact.html
        for analysis in self.result:
            # Skip p value calculation if no genes are found
            if analysis.study_count > 0:
                a_var: int = analysis.study_count
                b_var: int = study_n - analysis.study_count
                c_var: int = analysis.pathway_genes_count - analysis.study_count
                d_var: int = absolute_pathway_genes - analysis.pathway_genes_count - b_var

                # Calculate p value with Fisher exact test
                _, pval = stats.fisher_exact(
                    [
                        [a_var, b_var],
                        [c_var, d_var],
                    ]
                )

                analysis.pvalue = pval

        return self.result

    def to_json(self) -> list[dict[str, Any]]:
        """Export to json dict.

        :rtype: typing.List[typing.Dict[str, typing.Any]]
        :return: Json dict of enrichment results.
        """
        self._check_analysis_result_exist()

        result: list = []

        for item in self.result:
            result.append(item.json_summary())

        return result

    def to_csv(
        self,
        file_obj: str | IOBase | Any,
        delimiter: str = "\t",
        overwrite: bool = False,
    ) -> None:
        """Save result summary as file.

        :param typing.Union[str, io.IOBase, typing.Any] file_obj: String to file or IOBase object
        :param str delimiter: Deleimiter used for csv.
        :param bool overwrite: Set to True to overwrite file, if already exist.
        """
        # Check if summary exists
        self._check_analysis_result_exist()

        csv_file: IOBase | None = None

        if isinstance(file_obj, str):
            # file is str (Name of file)
            if os.path.isfile(file_obj) and not overwrite:
                raise RuntimeError(f"File {file_obj} does already exist.To solve please set overwrite=True.")

            csv_file = open(file_obj, mode="w", encoding="utf-8")
        elif isinstance(file_obj, IOBase):
            # file is IOBase (File object stream)
            csv_file = file_obj

        else:
            raise TypeError("Argument 'file_obj' must be string or IOBase instance, like an open file object.")

        # Delimiter of gene names
        child_delimiter = " "

        # Change child delimiter to aviod csv conficts
        if child_delimiter == delimiter:
            raise ValueError("This delimiter is reserved to seperate list of genes.")

        headers: list[str] = EnrichmentResult.get_header()
        writer: DictWriter = DictWriter(csv_file, fieldnames=headers, delimiter=delimiter)

        for item in self.result:
            # Write lines
            writer.writerow(item.json_summary(gene_delimiter=child_delimiter))

        csv_file.close()

    def to_dataframe(self) -> Any:
        """Return analysis result as pandas DataFrame. Required pandas dependency.

        :return: Export enrichment results as pandas dataframe.
        :rtype: pandas.DataFrame
        """
        # Ignore import lint at this place to keep pandas an optional dependency
        import pandas

        # Check if summary exists
        self._check_analysis_result_exist()
        summary_list = []
        for result in self.result:
            summary_list.append(result.json_summary())
        return pandas.DataFrame(summary_list)


def plot_enrichment_result(
    enrichment: Enrichment,
    ax: Axes | None = None,
    figsize: tuple[int, int] = (7, 7),
    cmap: str = "coolwarm",
    min_study_count: int = 1,
    max_pval: float | None = None,
    use_percent_study_count: bool = True,
) -> Axes:
    """Plot enrichment results."""
    result_df = enrichment.to_dataframe()

    # Filter out pathways with no genes found
    result_df = result_df[result_df["study_count"] >= min_study_count]

    if max_pval is not None:
        result_df = result_df[result_df["pvalue"] <= max_pval]

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    x_values = result_df["study_count"]
    x_label = "genes in study"

    if use_percent_study_count is True:
        x_values = x_values / result_df["pathway_genes"] * 100
        x_label = "genes in study [%]"

    scatter = ax.scatter(
        x=x_values,
        y=result_df["pathway_title"],
        c=[-math.log10(x) for x in result_df["pvalue"]],
        cmap=cmap,
    )

    cbar = plt.colorbar(scatter)
    cbar.set_label("- log10(p value)")
    ax.set_xlabel(x_label)
    ax.grid(visible=None)

    return ax
