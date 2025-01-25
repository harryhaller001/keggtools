"""Testing keggtools analysis module."""

import os
from io import StringIO
from typing import Any

import pandas
import pytest

from keggtools import Enrichment, EnrichmentResult, Pathway
from keggtools.storage import Storage


def test_enrichment_result() -> None:
    """Testing enrichment result instance."""
    result: EnrichmentResult = EnrichmentResult(
        org="mmu",
        pathway_id="12345",
        pathway_name="test",
        pathway_genes=["gene1", "gene2", "gene3", "gene4"],
        found_genes=["gene1", "gene2"],
    )

    # Testing computed properties
    assert result.pathway_genes_count == 4
    assert result.study_count == 2

    assert isinstance(result.__str__(), str)

    # testing result dict
    result_json: dict[str, Any] = result.json_summary()

    assert result_json["found_genes"] == "gene1,gene2"

    assert isinstance(result.get_header(), list)


def test_enrichment(storage: Storage) -> None:
    """Testing enrichment analysis instance."""
    # Load testing pathway
    with open(os.path.join(os.path.dirname(__file__), "pathway.kgml"), encoding="utf-8") as file_obj:
        loaded_pathway: Pathway = Pathway.from_xml(file_obj.read())

    # Build pathway list
    pathway_list: list[Pathway] = [loaded_pathway]

    enrichment: Enrichment = Enrichment(pathways=pathway_list)

    with pytest.raises(ValueError):
        enrichment._check_analysis_result_exist()

    results: list[EnrichmentResult] = enrichment.run_analysis(gene_list=["12043", "18035", "17874", "21937"])

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
    export_json: list[dict[str, Any]] = enrichment.to_json()

    assert isinstance(export_json, list) and isinstance(export_json[0], dict)

    assert export_json[0]["pvalue"] == 1.0
    assert export_json[0]["pathway_id"] == "04064"

    # Testing pandas dataframe export
    assert isinstance(enrichment.to_dataframe(), pandas.DataFrame)

    # Testing export to csv
    buffer: StringIO = StringIO()
    enrichment.to_csv(file_obj=buffer)

    # Testing invalid arguments
    with pytest.raises(TypeError):
        enrichment.to_csv(file_obj=None)

    # Testing export to csv by path arument
    # Use storage fixture to make sure generated files are removed savly
    csv_filename: str = storage.build_cache_path(filename="export.csv")
    enrichment.to_csv(file_obj=csv_filename, delimiter="\t")

    assert os.path.isfile(csv_filename)

    # Testing valid csv by reading exported csv
    validate_df: pandas.DataFrame = pandas.read_csv(csv_filename, delimiter="\t", header=None)

    # Check if gene list (5th column of csv file) contains seperated list of genes
    # TODO: make better test!
    assert len(str(validate_df.iat[0, 6]).split(" ")) == 4

    # Check error of space is used as delimiter
    with pytest.raises(ValueError):
        enrichment.to_csv(file_obj=csv_filename, delimiter=" ", overwrite=True)

    # Raises runtime error if file already exist
    with pytest.raises(RuntimeError):
        enrichment.to_csv(file_obj=csv_filename)

    # Raises no error if overwrite is set to true
    enrichment.to_csv(file_obj=csv_filename, overwrite=True)
