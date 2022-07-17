""" Testing parsing models """

from xml.etree import ElementTree

import pytest

from keggtools.models import (
    Relation,
    Entry,
    Pathway,
    Subtype,
    Component,
    Graphics,
    is_valid_pathway_name,
    is_valid_pathway_number,
    is_valid_pathway_org,
    is_valid_hex_color,
)



def test_valid_pathway_org() -> None:
    """
    Testing org code validation function.
    """

    # Testing valid cases
    assert is_valid_pathway_org(value="ko")
    assert is_valid_pathway_org(value="ec")
    assert is_valid_pathway_org(value="hsa")

    # Test invalid cases
    assert is_valid_pathway_org(value="hs2") is False
    assert is_valid_pathway_org(value="") is False
    assert is_valid_pathway_org(value="hsaa") is False



def test_valid_pathway_name() -> None:
    """
    Testing validation for combined pathway name.
    """

    # testing valid cases
    assert is_valid_pathway_name(value="path:ko12345")

    # Testing invalid cases (wrong prefix, invalid org and name)
    assert is_valid_pathway_name(value="prefix:ko12345") is False
    assert is_valid_pathway_name(value="path:aaaa12345") is False
    assert is_valid_pathway_name(value="path:ko123456") is False



def test_valid_pathway_number() -> None:
    """
    Testing validation of pathway number.
    """

    # Testing valid cases
    assert is_valid_pathway_number(value="12345")

    # Testing invalid cases (not numeric, not 5 digit)
    assert is_valid_pathway_number(value="1234a") is False
    assert is_valid_pathway_number(value="1234") is False



def test_valid_hex_color() -> None:
    """
    Testing validation of hex color.
    """

    # testing valid cases
    assert is_valid_hex_color(value="#00af4e")
    assert is_valid_hex_color(value="#00FFA4")

    # Testing invalid cases

    assert is_valid_hex_color(value="#00af4E00") is False
    assert is_valid_hex_color(value="#00af4K") is False




def test_relation_model_parsing() -> None:
    """
    Testing parsing function of relation model.
    """

    # Check correct parsing

    relation_object: Relation = Relation.parse(ElementTree.fromstring(
        """<relation entry1="44" entry2="50" type="ECrel"></relation>"""
    ))

    assert relation_object.entry1 == "44"
    assert relation_object.entry2 == "50"
    assert relation_object.type == "ECrel"


    # Check for invalid type values
    with pytest.raises(ValueError):
        Relation.parse(ElementTree.fromstring(
            """<relation entry1="44" entry2="50" type="invalid-type"></relation>"""
        ))


    # Check for invalid entry value types
    with pytest.raises(ValueError):
        Relation.parse(ElementTree.fromstring(
            """<relation entry1="stringvalue" entry2="50" type="ECrel"></relation>"""
        ))

    with pytest.raises(ValueError):
        Relation.parse(ElementTree.fromstring(
            """<relation entry1="44" entry2="stringvalue" type="ECrel"></relation>"""
        ))


    # Test missing type attribute
    with pytest.raises(ValueError):
        Relation.parse(ElementTree.fromstring(
            """<relation entry1="44" entry2="50"></relation>"""
        ))



def test_relation_with_subtype_parsing() -> None:
    """
    Test relation parsing function with one or more subtypes.
    """


    relation_parsed: Relation = Relation.parse(ElementTree.fromstring(
        """<relation entry1="44" entry2="50" type="ECrel">
            <subtype name="activation" value="--&gt;"/>
            <subtype name="binding/association" value="---"/>
        </relation>"""
    ))

    assert len(relation_parsed.subtypes) == 2



def test_subtype_parsing() -> None:
    """
    testing parsing function of subtype object.
    """

    # Test valid cases
    subtype_parsed: Subtype = Subtype.parse(ElementTree.fromstring("""<subtype name="activation" value="--&gt;"/>"""))

    assert subtype_parsed.name == "activation"


    # Test missing attribute
    with pytest.raises(ValueError):
        Subtype.parse(ElementTree.fromstring("""<subtype></subtype>"""))

    # Test invalid subtype attributes
    with pytest.raises(ValueError):
        Subtype.parse(ElementTree.fromstring("""<subtype name="invalid" value="test"></subtype>"""))



def test_graphics_parsing() -> None:
    """
    Testing parsing function of graphics object.
    """

    # test valid cases

    graphics_parsed: Graphics = Graphics.parse(ElementTree.fromstring(
        """<graphics name="Pgm1, 3230402E02Rik, Pgm-1, Pgm2" fgcolor="#000000" bgcolor="#BFFFBF" type="rectangle"
        x="628" y="541" width="46" height="17"/>"""
    ))

    assert graphics_parsed.type == "rectangle"
    assert graphics_parsed.name == "Pgm1, 3230402E02Rik, Pgm-1, Pgm2"
    assert graphics_parsed.fgcolor == "#000000"
    assert graphics_parsed.bgcolor == "#BFFFBF"

    assert graphics_parsed.coords is None


    # test minimal attributes (no attributes are required)
    minimal_graphics_parsed: Graphics = Graphics.parse(ElementTree.fromstring(
        """<graphics />"""
    ))

    assert minimal_graphics_parsed.name is None


    # test invalid cases


    # Test invalid graphics type
    with pytest.raises(ValueError):
        Graphics.parse(ElementTree.fromstring("""<graphics type="invalid" />"""))


    # Test invalid hex color
    with pytest.raises(ValueError):
        Graphics.parse(ElementTree.fromstring("""<graphics bgcolor="invalid" />"""))

    with pytest.raises(ValueError):
        Graphics.parse(ElementTree.fromstring("""<graphics fgcolor="invalid" />"""))


    # test none numeric coords

    with pytest.raises(ValueError):
        Graphics.parse(ElementTree.fromstring("""<graphics x="string" />"""))

    with pytest.raises(ValueError):
        Graphics.parse(ElementTree.fromstring("""<graphics y="string" />"""))

    with pytest.raises(ValueError):
        Graphics.parse(ElementTree.fromstring("""<graphics width="string" />"""))

    with pytest.raises(ValueError):
        Graphics.parse(ElementTree.fromstring("""<graphics height="string" />"""))



def test_component_parsing() -> None:
    """
    Testing function to parse component object.
    """

    # Test valid case
    component_parsed: Component = Component.parse(item=ElementTree.fromstring("""<component id="123" />"""))

    assert component_parsed.id == "123"

    # Test invalid cases

    # Missing id attribute
    with pytest.raises(ValueError):
        Component.parse(item=ElementTree.fromstring("""<component />"""))

    # Empty id attribute
    with pytest.raises(ValueError):
        Component.parse(item=ElementTree.fromstring("""<component id="" />"""))




def test_entry_parsing() -> None:
    """
    Testing function to parse entry object.
    """

    entry_parsed: Entry = Entry.parse(ElementTree.fromstring(
        """<entry id="123" name="entry name" type="gene"></entry>"""
    ))

    assert entry_parsed.id == "123"
    assert entry_parsed.type == "gene"

    assert entry_parsed.graphics is None




def test_pathway_parsing() -> None:
    """
    Testing function to parse pathway object.
    """

    # Test valid cases

    pathway_parsed: Pathway = Pathway.parse(ElementTree.fromstring(
        """<pathway name="path:mmu05205" org="mmu" number="05205"
         title="Proteoglycans in cancer"></pathway>"""
    ))

    assert pathway_parsed.org == "mmu"
    assert pathway_parsed.name == "path:mmu05205"

    assert pathway_parsed.link is None
    assert pathway_parsed.image is None


    # Test invalid cases

    # Check error on missing required attributes

    with pytest.raises(ValueError):
        Pathway.parse(ElementTree.fromstring(
            """<pathway org="mmu" number="05205"></pathway>"""
        ))


    with pytest.raises(ValueError):
        Pathway.parse(ElementTree.fromstring(
            """<pathway name="path:mmu05205" number="05205"></pathway>"""
        ))


    with pytest.raises(ValueError):
        Pathway.parse(ElementTree.fromstring(
            """<pathway name="path:mmu05205" org="mmu"></pathway>"""
        ))

    # Check argument mismatch error
    # All attributes of pathway xml have the correct format, but the combination of number and organism
    # don't match the pathway name

    with pytest.raises(ValueError):
        Pathway.parse(ElementTree.fromstring(
            """<pathway name="path:mmu05205" org="mmu" number="12345"></pathway>"""
        ))



    # Check invalid (malformatted) org, name and number arguments

    with pytest.raises(ValueError):
        Pathway(name="invalid:mmu12345", org="mmu", number="12345")

    with pytest.raises(ValueError):
        Pathway(name="path:mmu12345", org="mmuu", number="12345")

    with pytest.raises(ValueError):
        Pathway(name="path:mmu12345", org="mmu", number="123456")


