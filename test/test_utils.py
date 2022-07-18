""" Testing utils module """

from typing import Dict, List
from xml.etree.ElementTree import Element

# import pytest

# from requests.exceptions import HTTPError

# import responses
# from responses import Response


from keggtools.utils import (
    ColorGradient,
    parse_tsv,
    parse_xml,
    parse_tsv_to_dict,
)



def test_xml_parsing_wrapper() -> None:
    """
    Testing function to wrap XML element parser.
    """


    xml_string: str = "<hello>world</hello>"

    element: Element = parse_xml(xml_object_or_string=xml_string)

    assert isinstance(element, Element) is True
    assert element.tag == "hello"

    assert isinstance(parse_xml(xml_object_or_string=element), Element)



def test_attribute_checks() -> None:
    """
    Test XML element attribute check functions.
    """



def test_color_gradient() -> None:
    """
    Testing color gradient class.
    """

    # Test color tuple to css color string
    assert ColorGradient.to_css(color=(0, 0, 255)) == "rgb(0,0,255)"

    # Test color tuple to hex color string
    assert ColorGradient.to_hex(color=(0, 0, 255)) == "#0000ff"


    grad: ColorGradient = ColorGradient(
        start=(0, 0, 0),
        stop=(255, 255, 255),
        steps=255,
    )

    # Generate list of hex colors
    color_list: List[str] = grad.get_list()

    assert len(color_list) == 256

    # Check for correct colors
    assert color_list[0] == "#000000"
    assert color_list[255] == "#ffffff"

    # Check for random gray scale color
    assert color_list[123] == ColorGradient.to_hex(color=(123, 123, 123))


def test_parse_tsv() -> None:
    """
    Testing TSV parsing function.
    """

    tsv_data: str = "header1\theader2\nitem1\titem2\nitem3\titem4\n"

    parsed_data: list = parse_tsv(data=tsv_data)

    assert len(parsed_data) == 3
    assert parsed_data[0][1] == "header2"


    # Test parse to dict function

    parsed_dict: Dict[str, str] = parse_tsv_to_dict(data=tsv_data)

    assert parsed_dict["header1"] == "header2"
    assert parsed_dict["item3"] == "item4"



# @responses.activate
# def test_request_function() -> None:
#     """
#     Testing function to request string from url endpoint.
#     """

#     url: str = "http://example.com"
#     payload: str = "ok"

#     # Test valid response
#     test_response_1: Response = Response(method="GET", url=url, body=payload, status=200)
#     responses.add(test_response_1)
#     assert request(url=url) == payload

#     # test invalid response
#     test_response_2: Response = Response(method="GET", url=url, body=payload, status=400)
#     responses.add(test_response_2)

#     with pytest.raises(HTTPError):
#         request(url=url)
