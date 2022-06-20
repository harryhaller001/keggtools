""" Testing utils module """

import logging

from typing import List

from keggtools.utils import ColorGradient


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

