""" Testing keggtools rendering module """

import os
from typing import Any

from keggtools import Renderer, Pathway


def test_rendering_function() -> None:
    """
    testing rendering function with test KGML pathway.
    """

    with open(os.path.join(os.path.dirname(__file__), "pathway.kgml"), "r", encoding="utf-8") as file_obj:
        pathway: Pathway = Pathway.parse(file_obj.read())

    renderer: Renderer = Renderer(kegg_pathway=pathway, gene_dict={})

    renderer.render()

    assert isinstance(renderer.to_string(), str)

    binary_data: Any = renderer.export(extension="png")

    assert isinstance(binary_data, bytes)


