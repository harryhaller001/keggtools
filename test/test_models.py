""" Testing parsing models """

from xml.etree import ElementTree
from xml.etree.ElementTree import Element

import pytest

from keggtools.models import Relation


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
        Relation.parse(ElementTree.fromstring("""<relation entry1="44" entry2="50"></relation>"""))