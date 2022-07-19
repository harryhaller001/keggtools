""" Testing keggtools rendering module """
# pylint: disable=unused-import

from typing import Any, Dict

import pytest

from keggtools import Renderer, Pathway
from keggtools.models import is_valid_hex_color

from .fixtures import pathway


def test_rendering_function(pathway: Pathway) -> None:
    """
    testing rendering function with test KGML pathway.
    """

    # pylint: disable=redefined-outer-name

    renderer: Renderer = Renderer(kegg_pathway=pathway)

    renderer.render()

    # testing export dot string function
    assert isinstance(renderer.to_string(), str)

    # Testing binary export and supported file formats
    for extension in ("png", "jpeg", "svg", "pdf"):
        assert isinstance(renderer.to_binary(extension=extension), bytes)



def test_color_gradient_rendering(pathway: Pathway) -> None:
    """
    Testing color overlay from gene expression levels.
    """

    # pylint: disable=redefined-outer-name

    # Init example gene dict to test color generation
    gene_dict: Dict[str, float] = {
        "gene1": 0.0,
        "gene2": -5.1,
        "gene3": 1.2,
        "gene4": 3.4,
        "gene5": 2.3,
    }

    renderer: Renderer = Renderer(kegg_pathway=pathway, gene_dict=gene_dict)

    # Check default return color
    assert renderer.get_gene_color(gene_id="invalid") == "#ffffff"

    # Check default color on 0.0 expression
    assert renderer.get_gene_color(gene_id="gene1") == "#ffffff"

    # Testing custom default color from tuple
    assert renderer.get_gene_color(gene_id="gene1", default_color=(0, 0, 0)) == "#000000"


    # Test maximum
    assert is_valid_hex_color(renderer.get_gene_color("gene4")) and \
        renderer.get_gene_color("gene4").lower() == "#ff0000"

    # test minimum
    assert is_valid_hex_color(renderer.get_gene_color("gene2")) and \
        renderer.get_gene_color("gene2").lower() == "#0000ff"
