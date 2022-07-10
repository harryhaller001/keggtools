""" Testing parsing models """

from xml.etree import ElementTree
# from xml.etree.ElementTree import Element

import pytest

from keggtools.models import (
    Relation,
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



