

from keggtools.models import KEGGPathway
from keggtools.resolver import KEGGPathwayResolver
from keggtools.analysis import KEGGPathwayAnalysisResult, KEGGPathwayAnalysis
from keggtools.render import KEGGPathwayRenderer
from keggtools.storage import KEGGDataStorage



# Get all components
components = KEGGPathwayResolver.get_components()

# List all pathways
organism_id = "hsa"

# Resolve list of pathways
resolver = KEGGPathwayResolver(organism_id)
pathways = resolver.get_pathway_list()



if __name__ == "__main__":
    pass

