"""Testing keggtools rendering module."""

from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from keggtools.models import Pathway
from keggtools.render import Renderer, generate_embedded_html_table
from keggtools.utils import is_valid_hex_color


def test_generate_html_table() -> None:
    """Testing function to generate html table."""
    items: dict[str, str] = {
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


def test_rendering_function(pathway: Pathway) -> None:
    """Testing rendering function with test KGML pathway."""
    renderer: Renderer = Renderer(kegg_pathway=pathway)

    renderer.render()

    # testing export dot string function
    assert isinstance(renderer.to_string(), str)

    # Testing binary export and supported file formats
    for extension in ("png", "jpeg", "svg", "pdf"):
        assert isinstance(renderer.to_binary(extension=extension), bytes)


# TODO: resolving of mising entry names not implemented yet
# def test_rendering_with_resolve(
#     pathway: Pathway,
#     ) -> None:
#     """
#     Testing rendering function and resolving of missing gene names.
#     """

#     with RequestsMock() as mocked_request:

#         mocked_request.add(
#             method=HTTP_METHOD_GET,
#             url=re.compile(r"http://rest.kegg.jp/list/(.*)"),
#             body="mmu:11797\tBirc2, AW146227\n" \
#                 "mmu:266632\tIrak4, 8430405M07Rik\n" \
#                 "mmu:22033\tTraf5; TNF receptor-associated factor 5\n" \
#                 "mmu:108723\tCard11, 0610008L17Rik\n" \
#                 "mmu:170720\tCard14, Bimp2\n" \
#                 "mmu:22030\tTraf2, AI325259; TNF receptor-associated factor 2\n" \
#                 "mmu:66724\tTab3, 4921526G09Rik\n" \
#                 "mmu:68652\tTab2, 1110030N06Rik\n" \
#                 "mmu:22034\tTraf6, 2310003F17Rik\n" \
#                 "mmu:13000\tCsnk2a2, 1110035J23Rik\n" \
#                 "mmu:13001\tCsnk2b, CK_II_beta; casein kinase 2\n" \
#                 "mmu:12045\tBcl2a1b, A1-b; B cell leukemia/lymphoma 2 related protein A1b\n" \
#                 "mmu:12046\tBcl2a1c, A1-c; B cell leukemia/lymphoma 2 related protein A1c\n" \
#                 "mmu:12047\tBcl2a1d, A1-d; B cell leukemia/lymphoma 2 related protein A1d\n" \
#                 "mmu:20310\tCxcl2, CINC-2a\n" \
#                 "mmu:330122\tCxcl3, Dcip1\n" \
#                 "mmu:100042493\tCcl21b, 6CKBAC1\n" \
#                 "mmu:100504239\tGm10591, 6Ckine\n" \
#                 "mmu:100504346\tGm13304, 6Ckine\n" \
#                 "mmu:100862177\tCcl21d, 6Ckine\n" \
#                 "mmu:18829\tCcl21a, 6CKBAC2\n" \
#                 "mmu:24047\tCcl19, CKb11\n"
#         )

#         renderer: Renderer = Renderer(kegg_pathway=pathway)

#         renderer.render(resolve_unlabeled_genes=True)

#         # TODO: check if genes got resolved


def test_color_gradient_rendering(pathway: Pathway) -> None:
    """Testing color overlay from gene expression levels."""
    # Init example gene dict to test color generation
    gene_dict: dict[str, float] = {
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
    assert (
        is_valid_hex_color(renderer.get_gene_color("gene4")) and renderer.get_gene_color("gene4").lower() == "#ff0000"
    )

    # test minimum
    assert (
        is_valid_hex_color(renderer.get_gene_color("gene2")) and renderer.get_gene_color("gene2").lower() == "#0000ff"
    )
