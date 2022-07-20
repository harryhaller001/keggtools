""" Testing keggtools rendering module """

from typing import Dict

from xml.etree.ElementTree import Element
from xml.etree import ElementTree

from keggtools.models import is_valid_hex_color, Pathway
from keggtools.render import Renderer, generate_embedded_html_table

from .fixtures import pathway # pylint: disable=unused-import


def test_generate_html_table() -> None:
    """
    Testing function to generate html table.
    """

    items: Dict[str, str] = {
        "gene1": "#ffffff",
        "gene2": "#ff0000",
        "gene3": "#ffffff",
    }

    # Testing table string generation
    table_string: str = generate_embedded_html_table(items=items)

    assert isinstance(table_string, str)

    # test if string is valid html and contains all items
    # Invalid xhtml should raise parsing error
    parsed: Element = ElementTree.fromstring(table_string)

    assert parsed.tag == "table"

    for row_child in parsed:
        assert row_child.tag == "tr"

        # TODO: check if all items have table cells




def test_rendering_function(
    pathway: Pathway, # pylint: disable=redefined-outer-name
    ) -> None:
    """
    testing rendering function with test KGML pathway.
    """

    renderer: Renderer = Renderer(kegg_pathway=pathway)

    renderer.render()

    # testing export dot string function
    assert isinstance(renderer.to_string(), str)

    # Testing binary export and supported file formats
    for extension in ("png", "jpeg", "svg", "pdf"):
        assert isinstance(renderer.to_binary(extension=extension), bytes)



def test_color_gradient_rendering(
    pathway: Pathway, # pylint: disable=redefined-outer-name
    ) -> None:
    """
    Testing color overlay from gene expression levels.
    """

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
