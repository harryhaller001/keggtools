""" Testing keggtools analysis module """

from io import StringIO
import os
from typing import Any, Dict, List

import pytest
import pandas

from keggtools import Enrichment, EnrichmentResult, Pathway



def test_enrichment_result() -> None:
    """
    Testing enrichment result instance.
    """

    result: EnrichmentResult = EnrichmentResult(
        org="mmu",
        pathway_id="12345",
        pathway_name="test",
        pathway_genes=["gene1", "gene2", "gene3", "gene4"],
        found_genes=["gene1", "gene2"]
    )

    # Testing computed properties
    assert result.pathway_genes_count == 4
    assert result.study_count == 2

    assert isinstance(result.__str__(), str)


    # testing result dict
    result_json: Dict[str, Any] = result.json_summary()

    assert result_json["found_genes"] == "gene1,gene2"


    assert isinstance(result.get_header(), list)



def test_enrichment() -> None:
    """
    Testing enrichment analysis instance.
    """

    # Load testing pathway
    with open(os.path.join(os.path.dirname(__file__), "pathway.kgml"), "r", encoding="utf-8") as file_obj:
        loaded_pathway: Pathway = Pathway.parse(file_obj.read())

    # Build pathway list
    pathway_list: List[Pathway] = [loaded_pathway]

    enrichment: Enrichment = Enrichment(pathways=pathway_list)

    with pytest.raises(ValueError):
        # pylint: disable=protected-access
        enrichment._check_analysis_result_exist()


    results: List[EnrichmentResult] = enrichment.run_analysis(
        gene_list=["mmu:12043", "mmu:18035", "mmu:17874", "mmu:21937"]
    )

    assert len(results) == 1
    assert results[0].study_count == 4

    assert results[0].pvalue == 1.0


    # Testing subset function for result
    assert len(enrichment.get_subset(subset=["04064"])) == 1
    assert len(enrichment.get_subset(subset=["12345"])) == 0

    # testing subset and inplace
    enrichment.get_subset(subset=["04064"], inplace=True)
    assert len(enrichment.result) == 1



    # Test export functions

    # Testing json export
    export_json: List[Dict[str, Any]] = enrichment.to_json()

    assert isinstance(export_json, list) and isinstance(export_json[0], dict)

    assert export_json[0]["pvalue"] == 1.0
    assert export_json[0]["pathway_id"] == "04064"

    # Testing pandas dataframe export
    export_df: pandas.DataFrame = enrichment.to_dataframe()

    assert isinstance(export_df, pandas.DataFrame)


    # Testing export to csv
    buffer: StringIO = StringIO()
    enrichment.to_csv(file_obj=buffer)


    # TODO: testing export csv to file by path argument
    # enrichment.to_csv(file_obj="")

    # TODO: test delimiter char

    # TODO: test if csv is valid



    # Testing invalid arguments
    with pytest.raises(TypeError):
        enrichment.to_csv(file_obj=None)


