""" Basic utils for HTTP requests, parsing and rendering """


# import logging
# import math
import csv
from io import StringIO
from lib2to3.pgen2.token import OP

from typing import Any, List, Optional, Tuple, Union
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
# from tqdm import tqdm

import requests



# XML parsing helper functions

def get_numeric_attribute(element: Element, key: str) -> str:
    """
    Get attribute from XML Element object. Raises KeyError is Attribute is not found or not valid.
    """
    if is_valid_numeric_attribute(element=element, key=key) is False:
        raise KeyError(f"Value of attribute '{key}' is not a valid numeric string.")

    value: Optional[str] = element.attrib.get(key)

    # TODO: complete parsing function!!!

    if value is None or isinstance(value, str) is False:
        pass

    return value

def is_valid_attribute(element: Element, key: str) -> bool:
    """
    Check is attribute of XML element exist and is string.
    """
    return element.attrib.get(key) is not None and \
        isinstance(element.attrib.get(key), str) is True


def is_valid_numeric_attribute(element: Element, key: str) -> bool:
    """
    Check is attribute of XML element is numeric string.
    """
    return is_valid_attribute(element=element, key=key) and \
        str.isnumeric(element.attrib.get(key)) is True




def parse_xml(xml_object_or_string: Union[str, Element]) -> Element:
    """
    Returns XML Element object from string or XML Element.
    """
    if isinstance(xml_object_or_string, str):
        return ElementTree.fromstring(xml_object_or_string)
    return xml_object_or_string


# class Downloader:
#     """
#     URL Downloader
#     """

#     def __init__(self, url: str):
#         """
#         Init Downloader
#         :param url: str
#         """
#         self.url = url
#         self.filename = ""


#     def set_filename(self, filename: str):
#         """
#         Set filename for output
#         :param filename: str
#         """
#         self.filename = filename

#     def run(self):
#         """
#         Run Downloader
#         """
#         if not self.filename:
#             raise ValueError("Output filename not set!")

#         if not self.url:
#             raise ValueError("Url not set.")

#         # Streaming, so we can iterate over the response.
#         response = requests.get(self.url, stream=True)

#         # Total size in bytes.
#         total_size = int(response.headers.get('content-length', 0))
#         block_size = 1024
#         wrote = 0

#         with open(self.filename, 'wb') as f_obj:
#             for data in tqdm(response.iter_content(block_size),
#                              total=math.ceil(total_size // block_size),
#                              unit='KB',
#                              unit_scale=True):

#                 wrote = wrote + len(data)
#                 f_obj.write(data)
#         # if total_size != 0 and wrote != total_size:
#         if total_size not in (0, wrote):
#             logging.error("ERROR, something went wrong")




def parse_tsv(data: str) -> list:
    """
    Parse .tsv file from string
    :param data: str
    :return: list
    """
    fstream = StringIO(data)
    return list(csv.reader(fstream, delimiter="\t"))



def request(url: str, encoding="utf-8") -> str:
    """
    Small request GET method. Returns content as string.
    :param url: str
    :param encoding: str
    :return: str
    """
    # logging.debug("Requesting Url %s", url)
    response = requests.get(url=url)
    # logging.debug("Request finished with status code %d", response.status_code)
    response.raise_for_status()
    return response.content.decode(encoding)


# TODO: add request_tsv function for GET request and TSV parsing
def request_tsv(url: str) -> list:
    """
    Request and parse TSV file from url.
    """
    return parse_tsv(data=request(url=url))



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

        return tuple([int(item) for item in values])


