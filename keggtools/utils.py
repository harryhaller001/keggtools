""" Basic utils for HTTP requests, parsing and rendering """


import logging
import math
import os
from datetime import datetime
import csv
from io import StringIO
from tqdm import tqdm
import requests
# from typing import Optional, Union, Any, Iterable



def getcwd():
    """
    Return dirname of package file
    :returnr: str
    """
    # return os.path.split(__file__)[0]
    return os.path.dirname(__file__)


def get_timestamp():
    """
    Return timestamp
    :return: datetime
    """
    return datetime.now().timestamp()


# Code using from
# https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
# Thanks to Ned Batchelder (https://stackoverflow.com/users/14343/ned-batchelder)
def chunks(items: list, count: int):
    """
    Yield successive count-sized chunks from items.
    """
    for index in range(0, len(items), count):
        yield items[index:index + count]


class Downloader:
    """
    URL Downloader
    """

    def __init__(self, url: str):
        """
        Init Downloader
        :param url: str
        """
        self.url = url
        self.filename = ""


    def set_filename(self, filename: str):
        """
        Set filename for output
        :param filename: str
        """
        self.filename = filename

    def run(self):
        """
        Run Downloader
        """
        if not self.filename:
            raise ValueError("Output filename not set!")

        if not self.url:
            raise ValueError("Url not set.")

        # Streaming, so we can iterate over the response.
        response = requests.get(self.url, stream=True)

        # Total size in bytes.
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024
        wrote = 0

        with open(self.filename, 'wb') as f_obj:
            for data in tqdm(response.iter_content(block_size),
                             total=math.ceil(total_size // block_size),
                             unit='KB',
                             unit_scale=True):

                wrote = wrote + len(data)
                f_obj.write(data)
        # if total_size != 0 and wrote != total_size:
        if total_size not in (0, wrote):
            logging.error("ERROR, something went wrong")




def parse_tsv(data: str):
    """
    Parse .tsv file from string
    :param data: str
    :return: list
    """
    if isinstance(data, str):
        fstream = StringIO(data)
    else:
        raise TypeError("Type of 'data' must be str or bytes.")

    return list(csv.reader(fstream, delimiter="\t"))



def request(url: str, encoding="utf-8"):
    """
    Small request GET method. Returns string.
    :param url: str
    :param encoding: str
    :return: str
    """
    logging.info("Requesting Url %s", url)
    response = requests.get(url=url)
    logging.info("Request finished with status code %d", response.status_code)
    response.raise_for_status()
    content = response.content

    if isinstance(content, bytes):
        return content.decode(encoding)

    return content


class ColorGradient:
    """
    Create color gradient
    """

    def __init__(self, start: tuple, stop: tuple, steps: int):
        """
        Init ColorGradient
        :param start: tuple
        :param stop: tuple
        :param steps: int
        """
        self.start = start
        self.stop = stop
        self.steps = steps


    @staticmethod
    def to_css(color: tuple):
        """
        Convert color tuple to CSS rgb color string
        :param color: tuple
        :return: str
        """
        return "rgb({R},{G},{B})".format(R=color[0], G=color[1], B=color[2])


    def get_list(self):
        """
        Get Gradient Color as list
        :return: list
        """
        return [
            ColorGradient.list_to_hex(code) for code in ColorGradient._gradient(
                self.stop,
                self.start,
                self.steps)
                ]


    @staticmethod
    def _intermediate(a_var, b_var, ratio):
        def _array_multiply(array, c_var):
            return [element * c_var for element in array]

        a_component = _array_multiply(a_var, ratio)
        b_component = _array_multiply(b_var, 1 - ratio)
        return list(map(sum, zip(a_component, b_component)))


    @staticmethod
    def _gradient(a_var, b_var, steps):
        steps -= 1
        steps = [index / float(steps) for index in range(steps)]
        result = [ColorGradient._intermediate(a_var, b_var, step) for step in steps]
        result.append(a_var)
        return result


    @staticmethod
    def list_to_hex(code: list):
        """
        Convert color list to CSS hex color string
        :param code: list
        :return: str
        """
        return "#" + "".join(["{:02x}".format(int(num)) for num in code])


    def render_graphviz(self):
        """
        Testing function using graphviz
        :return: str
        """
        result = self.get_list()
        string = ["digraph G {"]
        for i in range(0, 20):
            # result[i]
            string.append("\tnode[color = \"{COLOR}\" style = filled] {N};".format(
                COLOR=result[i],
                N=i))

        string.append("\t" + " -> ".join([str(l) for l in range(0, 20)]))
        string.append("}")
        return "\n".join(string)


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    COLOR_GRADIENT = ColorGradient(start=(0, 179, 0), stop=(187, 0, 0), steps=20)
    print(COLOR_GRADIENT.get_list())
    print(COLOR_GRADIENT.render_graphviz())

    request("http://example.com/")
