""" Testing parsing models """

from xml.etree import ElementTree
from xml.etree.ElementTree import Element

import pytest

from keggtools.models import Relation, is_valid_org



def test_valid_org() -> None:
    """
    Testing org code validation function.
    """

    # Testing valid cases
    assert is_valid_org(value="ko")
    assert is_valid_org(value="ec")
    assert is_valid_org(value="hsa")

    # Test invalid cases
    assert is_valid_org(value="hs2") is False
    assert is_valid_org(value="") is False
    assert is_valid_org(value="hsaa") is False



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



