""" Unittest for KEGGTOOLS """
# pylint: disable=missing-function-docstring,wrong-import-position,unused-import

import logging
import os

CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
ORGANISM_ID = "hsa"

if os.path.isdir(CACHE_DIR):
    # TODO: remove caching directory before each run
    pass

os.environ["KEGG_DATA"] = CACHE_DIR


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
    components = KEGGPathwayResolver.get_components()

    # Check if compounds are cached and have correct content
    assert KEGGDataStorage.exist(filename="compound.dump") and \
        isinstance(components, dict) and \
        components["C22323"] == "alpha-N-Dichloroacetyl-p-aminophenylserinol"

    logging.info("compounds are requested, cached and have correct content")


def test_pathway_api_request():
    pathway_id = list(IMMUNE_SYSTEM_PATHWAYS.keys())[1]
    logging.info("Check pathway API request using %s ('%s')",
                 pathway_id,
                 IMMUNE_SYSTEM_PATHWAYS[pathway_id])

    # Resolve pathway
    resolver = KEGGPathwayResolver(org=ORGANISM_ID)
    pathway = resolver.get_pathway(code=pathway_id)
    logging.info(pathway.__str__())

    # Check if pathway is cached and is parse correct
    assert KEGGDataStorage.exist(filename=f"{ORGANISM_ID}_path{pathway_id}.kgml") and \
        pathway.org == ORGANISM_ID and \
        pathway.number == pathway_id and \
        len(pathway.relations) == 54 and \
        len(pathway.entries) == 74

    logging.info("pathway %s is requested, cached and parsed correct", pathway_id)


def test_organism_api_request():
    pass


def test_parsing():
    pass
    # logging.info("Check parsing of KEGG models")


def test_enrichment():
    pass


def test_rendering():
    pass



if __name__ == "__main__":
    test_parsing()
