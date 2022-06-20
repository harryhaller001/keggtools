""" Testing utils module """

from typing import List

from keggtools.utils import ColorGradient, parse_tsv


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

    parsed_data: list = parse_tsv(data="header1\theader2\nitem1\titem2\nitem3\titem4\n")

    assert len(parsed_data) == 3
    assert parsed_data[0][1] == "header2"

