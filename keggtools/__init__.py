""" Init keggtools module """


# TODO: change Analysis to Enrichment ?

from .analysis import Analysis, AnalysisResult
from .models import Pathway, Relation, Entry, Graphics, Subtype, Component
from .resolver import Resolver
from .render import Renderer

from .const import IMMUNE_SYSTEM_PATHWAYS

