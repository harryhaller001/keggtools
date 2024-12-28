"""Testing parsing models."""

import os
from xml.etree import ElementTree

import pytest

from keggtools.models import (
    Alt,
    Component,
    Entry,
    Graphics,
    Pathway,
    Product,
    Reaction,
    Relation,
    Substrate,
    Subtype,
)


def test_relation_model_parsing() -> None:
    """Testing parsing function of relation model."""
    # Check correct parsing

    relation_object: Relation = Relation.from_xml_tree(
        ElementTree.fromstring("""<relation entry1="44" entry2="50" type="ECrel"></relation>""")
    )

    assert relation_object.entry1 == "44"
    assert relation_object.entry2 == "50"
    assert relation_object.type == "ECrel"

    assert isinstance(relation_object.__str__(), str)

    # Check for invalid type values
    with pytest.raises(ValueError):
        Relation.from_xml_tree(
            ElementTree.fromstring("""<relation entry1="44" entry2="50" type="invalid-type"></relation>""")
        )

    # Check for invalid entry value types
    # with pytest.raises(ValueError):
    #     Relation.from_xml_tree(
    #         ElementTree.fromstring("""<relation entry1="stringvalue" entry2="50" type="ECrel"></relation>""")
    #     )

    # with pytest.raises(ValueError):
    #     Relation.from_xml_tree(
    #         ElementTree.fromstring("""<relation entry1="44" entry2="stringvalue" type="ECrel"></relation>""")
    #     )

    # Test missing type attribute
    # with pytest.raises(ValueError):
    #     Relation.from_xml_tree(ElementTree.fromstring("""<relation entry1="44" entry2="50"></relation>"""))


def test_relation_with_subtype_parsing() -> None:
    """Test relation parsing function with one or more subtypes."""
    relation_parsed: Relation = Relation.from_xml_tree(
        ElementTree.fromstring(
            """<relation entry1="44" entry2="50" type="ECrel">
            <subtype name="activation" value="--&gt;"/>
            <subtype name="binding/association" value="---"/>
        </relation>"""
        )
    )

    assert len(relation_parsed.subtypes) == 2


def test_subtype_parsing() -> None:
    """Testing parsing function of subtype object."""
    # Test valid cases
    subtype_parsed: Subtype = Subtype.from_xml_tree(
        ElementTree.fromstring("""<subtype name="activation" value="--&gt;"/>""")
    )

    assert subtype_parsed.name == "activation"

    assert isinstance(subtype_parsed.__str__(), str)

    # Test missing attribute
    with pytest.raises(ValueError):
        Subtype.from_xml_tree(ElementTree.fromstring("""<subtype></subtype>"""))

    # Test invalid subtype attributes
    with pytest.raises(ValueError):
        Subtype.from_xml_tree(ElementTree.fromstring("""<subtype name="invalid" value="test"></subtype>"""))

    # Testing subtype instance to XML
    assert subtype_parsed.to_xml_tree().attrib["name"] == "activation"
    assert subtype_parsed.to_xml_tree().tag == "subtype"


def test_graphics_parsing() -> None:
    """Testing parsing function of graphics object."""
    # test valid cases

    graphics_parsed: Graphics = Graphics.from_xml_tree(
        ElementTree.fromstring(
            """<graphics name="Pgm1, 3230402E02Rik, Pgm-1, Pgm2" fgcolor="#000000" bgcolor="#BFFFBF" type="rectangle"
        x="628" y="541" width="46" height="17"/>"""
        )
    )

    assert graphics_parsed.type == "rectangle"
    assert graphics_parsed.name == "Pgm1, 3230402E02Rik, Pgm-1, Pgm2"
    assert graphics_parsed.fgcolor == "#000000"
    assert graphics_parsed.bgcolor == "#BFFFBF"

    assert graphics_parsed.coords is None

    assert isinstance(graphics_parsed.__str__(), str)

    # test minimal attributes (no attributes are required)
    minimal_graphics_parsed: Graphics = Graphics.from_xml_tree(ElementTree.fromstring("""<graphics />"""))

    assert minimal_graphics_parsed.name is None

    # test invalid cases

    # Test invalid graphics type
    # with pytest.raises(ValueError):
    #     Graphics.from_xml_tree(ElementTree.fromstring("""<graphics type="invalid" />"""))

    # # Test invalid hex color
    # with pytest.raises(ValueError):
    #     Graphics.from_xml_tree(ElementTree.fromstring("""<graphics bgcolor="invalid" />"""))

    # with pytest.raises(ValueError):
    #     Graphics.from_xml_tree(ElementTree.fromstring("""<graphics fgcolor="invalid" />"""))

    # test none numeric coords

    # with pytest.raises(ValueError):
    #     Graphics.from_xml_tree(ElementTree.fromstring("""<graphics x="string" />"""))

    # with pytest.raises(ValueError):
    #     Graphics.from_xml_tree(ElementTree.fromstring("""<graphics y="string" />"""))

    # with pytest.raises(ValueError):
    #     Graphics.from_xml_tree(ElementTree.fromstring("""<graphics width="string" />"""))

    # with pytest.raises(ValueError):
    #     Graphics.from_xml_tree(ElementTree.fromstring("""<graphics height="string" />"""))

    # Testing coord parsing and xml dump
    graphics_with_coords: Graphics = Graphics.from_xml_tree(
        ElementTree.fromstring("""<graphics coords="573,729,573,779" />""")
    )

    assert isinstance(graphics_with_coords.coords, str)
    assert graphics_with_coords.to_xml_tree().attrib["coords"] == "573,729,573,779"


def test_component_parsing() -> None:
    """Testing function to parse component object."""
    # Test valid case
    component_parsed: Component = Component.from_xml_tree(ElementTree.fromstring("""<component id="123" />"""))

    assert component_parsed.id == "123"

    assert isinstance(component_parsed.__str__(), str)

    # Test invalid cases

    # Missing id attribute
    # with pytest.raises(ValueError):
    #     Component.from_xml_tree(ElementTree.fromstring("""<component />"""))

    # Empty id attribute
    # with pytest.raises(ValueError):
    #     Component.from_xml_tree(ElementTree.fromstring("""<component id="" />"""))


def test_entry_parsing() -> None:
    """Testing function to parse entry object."""
    # Test valid cases

    entry_parsed: Entry = Entry.from_xml_tree(
        ElementTree.fromstring("""<entry id="123" name="mmu:12048" type="gene"></entry>""")
    )

    assert entry_parsed.id == "123"
    assert entry_parsed.type == "gene"

    assert entry_parsed.graphics is None

    assert isinstance(entry_parsed.__str__(), str)

    assert entry_parsed.get_gene_id() == ["12048"]

    # Test invalid cases

    # with pytest.raises(ValueError):
    #     Entry(id="123", name="mmu:12048", type="invalid")


def test_entry_parsing_multiple_names() -> None:
    """Testing function to parse entry object with multiple gene names."""
    # Test valid cases
    entry_parsed: Entry = Entry.from_xml_tree(
        ElementTree.fromstring("""<entry id="123" name="mmu:12048 mmu:12049 mmu:12050" type="gene"></entry>""")
    )

    assert entry_parsed.has_multiple_names() is True


def test_pathway_parsing() -> None:
    """Testing function to parse pathway object."""
    # Test valid cases

    pathway_parsed: Pathway = Pathway.from_xml_tree(
        ElementTree.fromstring(
            """<pathway name="path:mmu05205" org="mmu" number="05205"
         title="Proteoglycans in cancer"></pathway>"""
        )
    )

    assert pathway_parsed.org == "mmu"
    assert pathway_parsed.name == "path:mmu05205"

    assert pathway_parsed.link is None
    assert pathway_parsed.image is None

    assert isinstance(pathway_parsed.__str__(), str)

    # Test invalid cases

    # Check error on missing required attributes

    with pytest.raises(ValueError):
        Pathway.from_xml_tree(ElementTree.fromstring("""<pathway org="mmu" number="05205"></pathway>"""))

    with pytest.raises(ValueError):
        Pathway.from_xml_tree(ElementTree.fromstring("""<pathway name="path:mmu05205" number="05205"></pathway>"""))

    with pytest.raises(ValueError):
        Pathway.from_xml_tree(ElementTree.fromstring("""<pathway name="path:mmu05205" org="mmu"></pathway>"""))

    # Check argument mismatch error
    # All attributes of pathway xml have the correct format, but the combination of number and organism
    # don't match the pathway name

    # with pytest.raises(ValueError):
    #     Pathway.from_xml_tree(
    #         ElementTree.fromstring("""<pathway name="path:mmu05205" org="mmu" number="12345"></pathway>""")
    #     )

    # Check invalid (malformatted) org, name and number arguments

    # with pytest.raises(ValueError):
    #     Pathway(name="invalid:mmu12345", org="mmu", number="12345")

    # with pytest.raises(ValueError):
    #     Pathway(name="path:mmu12345", org="mmuu", number="12345")

    # with pytest.raises(ValueError):
    #     Pathway(name="path:mmu12345", org="mmu", number="123456")


def test_reaction_parsing() -> None:
    """Testing function to parse XML to reaction."""
    # test correct parsing
    parsed_reaction = Reaction.from_xml("""
        <reaction id="29" name="rn:R01274" type="irreversible">
            <substrate id="86" name="cpd:C00154"/>
            <product id="87" name="cpd:C00249"/>
        </reaction>
    """)

    # Check values are parsed correctly
    assert parsed_reaction.id == "29"
    assert parsed_reaction.name == "rn:R01274"

    # Check correct types
    assert isinstance(parsed_reaction.substrates[0], Substrate)
    assert isinstance(parsed_reaction.products[0], Product)

    assert len(parsed_reaction.products) == 1 and parsed_reaction.products[0].name == "cpd:C00249"
    assert len(parsed_reaction.substrates) == 1 and parsed_reaction.substrates[0].name == "cpd:C00154"

    # Testing correct type of string conversion
    assert isinstance(parsed_reaction.__str__(), str)
    assert isinstance(parsed_reaction.products[0].__str__(), str)
    assert isinstance(parsed_reaction.substrates[0].__str__(), str)

    # Testing invalid reaction type
    # with pytest.raises(ValueError):
    #     Reaction(id="123", name="rn:R01274", type="invalid")

    # Testing reaction to xml
    reaction_string: str = ElementTree.tostring(parsed_reaction.to_xml_tree()).decode("utf-8")

    assert Reaction.from_xml_tree(ElementTree.fromstring(reaction_string)).name == parsed_reaction.name


def test_alt_element_parsing() -> None:
    """Testing parsing function of Alt element."""
    # Testing correct parsing of element
    parsed_product = Product.from_xml('<product id="87" name="cpd:C00249"><alt name="cpd:C00154"></alt></product>')

    assert parsed_product.alt is not None and isinstance(parsed_product.alt, Alt)
    assert parsed_product.alt.name == "cpd:C00154"

    # Testing correct parsing from substrate element
    parsed_substrate = Substrate.from_xml(
        """<substrate id="87" name="cpd:C00249"><alt name="cpd:C00155"></alt></substrate>"""
    )

    assert parsed_substrate.alt is not None and isinstance(parsed_substrate.alt, Alt)
    assert parsed_substrate.alt.name == "cpd:C00155"

    # Testing correct type of string conversion
    assert isinstance(parsed_product.alt.__str__(), str)

    # Testing xml build of alt element
    assert isinstance(parsed_substrate.to_xml(), str | bytes)
    assert parsed_substrate.alt.to_xml_tree().tag == "alt"
    assert parsed_substrate.alt.to_xml_tree().attrib["name"] == parsed_substrate.alt.name

    assert isinstance(parsed_product.to_xml(), str | bytes)
    assert parsed_product.alt.to_xml_tree().tag == "alt"
    assert parsed_product.alt.to_xml_tree().attrib["name"] == parsed_product.alt.name


def test_full_pathway_parsing() -> None:
    """Testing parsing functions by loading full KGML pathway."""
    # TODO: add parsing of reaction, products and substrates

    basedir: str = os.path.dirname(__file__)

    # Open pathway file and load content as string
    with open(os.path.join(basedir, "pathway.kgml"), encoding="utf-8") as file_obj:
        pathway_parsed: Pathway = Pathway.from_xml(file_obj.read())

    # Test search for entry in pathway

    found_entry: Entry | None = pathway_parsed.get_entry_by_id(entry_id="154")

    assert found_entry is not None
    assert found_entry.name == "mmu:19697"

    # Test search of none existing entry in pathway

    assert pathway_parsed.get_entry_by_id(entry_id="invalid") is None

    # test get gene list function
    # TODO: better checks (type, ...)

    gene_list: list[str] = pathway_parsed.get_genes()

    assert "19697" in gene_list


def test_kgml_to_xml(pathway: Pathway) -> None:
    """Testing generate and parsing from pathway instance."""
    # Testing KGML model to xml string
    xml_string: str | bytes = pathway.to_xml()
    assert isinstance(xml_string, str) or isinstance(xml_string, bytes)

    # Parsing XML string to pathway
    parsed_pathway: Pathway = Pathway.from_xml(xml_string)

    assert parsed_pathway.name == pathway.name
