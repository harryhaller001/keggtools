""" Unittest for KEGGTOOLS """
# pylint: disable=missing-function-docstring,wrong-import-position,unused-import

import logging
logging.basicConfig(level=logging.DEBUG)

import os
import shutil

CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
ORGANISM_ID = "hsa"

if os.path.isdir(CACHE_DIR):
    logging.debug("Cleaning up caching directory")
    # remove caching directory before each run
    for filename in os.listdir(CACHE_DIR):
        file_path = os.path.join(CACHE_DIR, filename)

        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)


os.environ["KEGG_DATA"] = CACHE_DIR


import pydot
from keggtools.analysis import KEGGPathwayAnalysis, KEGGPathwayAnalysisResult
from keggtools.render import KEGGPathwayRenderer
from keggtools.models import KEGGPathway, Entry, Relation, Graphics, Component
from keggtools.resolver import KEGGPathwayResolver
from keggtools.storage import KEGGDataStorage
from keggtools.const import KEGG_DATA, IMMUNE_SYSTEM_PATHWAYS


def test_env_variable():
    logging.info("Checking env variable KEGG_DATA ('%s')", KEGG_DATA)

    # Check if KEGG_DATA is overwritten with local caching dir
    assert CACHE_DIR == KEGG_DATA
    logging.info("Local overwrite of KEGG_DATA is working")


def test_component_api_request():
    logging.info("Check API request for compound")

    # Request compounds from API
    components = KEGGPathwayResolver.get_components()

    # Check if compounds are cached and have correct content
    assert KEGGDataStorage.exist(filename="compound.dump") and \
        isinstance(components, dict) and \
        components["C22323"] == "alpha-N-Dichloroacetyl-p-aminophenylserinol"

    logging.info("compounds are requested, cached and have correct content")


def test_organism_api_request():
    logging.info("Check if organism list API request")

    # Request organism list from API
    assert KEGGDataStorage.check_organism(org=ORGANISM_ID) and \
        KEGGDataStorage.exist(filename="organism.dump")

    # Check if organism code resolves correct
    organism_name = KEGGDataStorage.get_organism_name(org_code=ORGANISM_ID)
    assert organism_name == "Homo sapiens (human)"

    logging.info("Organism '%s' (%s) is in list. API request finshed and cached correct",
                 ORGANISM_ID,
                 organism_name)


def test_pathway_api_request():

    # request pathway list to check pathway id
    resolver = KEGGPathwayResolver(org=ORGANISM_ID)
    pathway_list = list(resolver.get_pathway_list().keys())

    # Select first immune system pathway as testing example
    pathway_id = list(IMMUNE_SYSTEM_PATHWAYS.keys())[1]
    logging.info("Check pathway API request using %s ('%s')",
                 pathway_id,
                 IMMUNE_SYSTEM_PATHWAYS[pathway_id])

    assert pathway_id in pathway_list
    logging.info("Pathway id in list of all pathways")

    # Resolve pathway
    pathway = resolver.get_pathway(code=pathway_id)
    logging.info(pathway.__str__())

    # Check if pathway is cached and is parse correct
    assert KEGGDataStorage.exist(filename=f"{ORGANISM_ID}_path{pathway_id}.kgml") and \
        pathway.org == ORGANISM_ID and \
        pathway.number == pathway_id and \
        len(pathway.relations) == 54 and \
        len(pathway.entries) == 74

    logging.info("pathway %s is requested, cached and parsed correct", pathway_id)


def test_enrichment():

    # Select first immune system pathway as testing example
    pathway_id = list(IMMUNE_SYSTEM_PATHWAYS.keys())[1]
    logging.info("Check enrichment analysis using %s ('%s')",
                 pathway_id,
                 IMMUNE_SYSTEM_PATHWAYS[pathway_id])

    # Resolve pathway
    resolver = KEGGPathwayResolver(org=ORGANISM_ID)
    pathway = resolver.get_pathway(code=pathway_id)
    logging.info(pathway.__str__())

    analysis = KEGGPathwayAnalysis(org=ORGANISM_ID, pathways=[pathway_id])

    # Get the 5 first genes from parsing
    sample_genes = [
        int(entry.get_gene_id()) for entry in pathway.entries[:10] if entry.type == "gene"]

    # perform enrichment analysis
    result = analysis.run_analysis(gene_list=sample_genes)[0]
    assert len(result.found_genes) == len(sample_genes) and \
        result.study_count == len(sample_genes) and \
        result.pvalue == 1.0

    logging.info("Enrichment analysis finished successful (%s, pvalue:%d)",
                 result.__str__(),
                 result.pvalue)


def test_rendering():

    # Select first immune system pathway as testing example
    pathway_id = list(IMMUNE_SYSTEM_PATHWAYS.keys())[1]
    logging.info("Check enrichment analysis using %s ('%s')",
                 pathway_id,
                 IMMUNE_SYSTEM_PATHWAYS[pathway_id])

    # Init pathway renderer with example pathway
    pathway = KEGGPathwayResolver(org=ORGANISM_ID).get_pathway(pathway_id)
    renderer = KEGGPathwayRenderer(kegg_pathway=pathway)

    # Create dot string
    dot_string = renderer.raw_render()
    assert dot_string is not None

    graphs = pydot.graph_from_dot_data(dot_string)
    graph = graphs[0]
    output_filename = os.path.join(CACHE_DIR, "tmp.png")
    graph.write_png(output_filename)

    assert os.path.isfile(output_filename)
    logging.info("Rendering of dot graph finished successful")


if __name__ == "__main__":
    test_env_variable()
    test_component_api_request()
    test_organism_api_request()
    test_pathway_api_request()
    test_enrichment()
    test_rendering()
