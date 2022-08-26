""" Init keggtools module """


__version__: str = "1.0.0"

from .analysis import EnrichmentResult, Enrichment
from .const import IMMUNE_SYSTEM_PATHWAYS
from .models import Pathway, Relation, Entry, Graphics, Subtype, Component
from .render import Renderer
from .resolver import Resolver
from .storage import Storage
from .utils import ColorGradient
