""" Basic utils for HTTP requests, parsing and rendering """

import csv
from io import StringIO

from typing import Dict, List, Optional, Union
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

import requests



# XML parsing helper functions


def get_attribute(element: Element, key: str) -> str:
    """
    Get attribute from XML Element object. Raises KeyError is Attribute is not found or not valid.
    """

    value: Optional[str] = element.attrib.get(key)

    # Check if value is not none and is string
    if value is None or isinstance(value, str) is False:
        raise ValueError(f"Value of attribute '{key}' is not a string.")

    return value



def get_numeric_attribute(element: Element, key: str) -> str:
    """
    Get attribute from XML Element object. Raises KeyError is Attribute is not found or not valid.
    """

    value: str = get_attribute(element=element, key=key)

    # Check if string is numeric
    if str.isnumeric(value) is False:
        raise ValueError(f"Value of attribute '{key}' is not numeric.")

    return value



def parse_xml(xml_object_or_string: Union[str, Element]) -> Element:
    """
    Returns XML Element object from string or XML Element.
    """
    if isinstance(xml_object_or_string, str):
        return ElementTree.fromstring(xml_object_or_string)
    return xml_object_or_string




def parse_tsv(data: str) -> list:
    """
    Parse .tsv file from string
    :param data: str
    :return: list
    """
    return list(csv.reader(StringIO(data), delimiter="\t"))



def parse_tsv_to_dict(data: str) -> Dict[str, str]:
    """
    Parse .tsv file from string and build dict from first two columns. Other columns are ignored.
    """
    list_data: list = parse_tsv(data=data)

    result: Dict[str, str] = {}

    for row in list_data:
        if len(row) >= 2 and row[0] != "":
            result[row[0]] = row[1]

        # TODO: handle else cases or ignore silent ?

    return result


def request(url: str, encoding="utf-8") -> str:
    """
    Small request GET method. Returns content as string.
    :param url: str
    :param encoding: str
    :return: str
    """
    response = requests.get(url=url)
    response.raise_for_status()
    return response.content.decode(encoding)



class ColorGradient:
    """
    Create color gradient.
    """

    def __init__(
        self,
        start: tuple,
        stop: tuple,
        steps: int
    ) -> None:
        """
        Init ColorGradient instance.
        :param start: Color tuple
        :param stop: Color tuple
        :param steps: Number of steps.
        """
        self.start: tuple = start
        self.stop: tuple = stop
        self.steps: int = steps


    @staticmethod
    def to_css(color: tuple) -> str:
        """
        Convert color tuple to CSS rgb color string.
        :param color: Color tuple containing 3 integers
        :return: str
        """
        # if len(color) != 3 or not all([isinstance(value, int) for value in color]):
        #     raise ValueError("Color must be a tuple of 3 integers.")

        return f"rgb({color[0]},{color[1]},{color[2]})".lower()


    @staticmethod
    def to_hex(color: tuple) -> str:
        """
        Convert color tuple to hex color string.
        """

        # TODO: check for int type.
        # TODO: check for 0-255 range

        return f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}".lower()


    def get_list(self) -> List[str]:
        """
        Get gradient color as list.
        :return: list
        """

        step_list = [index / float(self.steps) for index in range(self.steps)]
        result = [ColorGradient._intermediate(self.stop, self.start, step) for step in step_list]
        result.append(self.stop)


        return [
            ColorGradient.to_hex(code) for code in result
        ]


    @staticmethod
    def _intermediate(a_var: tuple, b_var: tuple, ratio: float) -> tuple:
        def _array_multiply(array, c_var):
            return [element * c_var for element in array]

        a_component = _array_multiply(a_var, ratio)
        b_component = _array_multiply(b_var, 1 - ratio)
        values: List[float] = list(map(sum, zip(a_component, b_component)))

        return tuple((int(item) for item in values))


