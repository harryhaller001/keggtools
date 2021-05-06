""" Basic utils for HTTP requests, parsing and rendering """


import logging
from tqdm import tqdm
import requests
import math
import os
from datetime import datetime
import csv
from io import StringIO
from typing import Optional, Union



def getcwd():
    # return os.path.split(__file__)[0]
    return os.path.dirname(__file__)


def get_timestamp():
    return datetime.now().timestamp()


# Code using from
# https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
# Thanks to Ned Batchelder (https://stackoverflow.com/users/14343/ned-batchelder)
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


class Downloader:
    def __init__(self, url: str):
        self.url = url
        self.output = ""

    def set_output(self, filename: str):
        self.output = filename

    def run(self):
        if not self.output:
            raise ValueError("output not set!")

        # Streaming, so we can iterate over the response.
        r = requests.get(self.url, stream=True)

        # Total size in bytes.
        total_size = int(r.headers.get('content-length', 0))
        block_size = 1024
        wrote = 0

        with open(self.output, 'wb') as f:
            for data in tqdm(r.iter_content(block_size),
                             total=math.ceil(total_size // block_size),
                             unit='KB',
                             unit_scale=True):

                wrote = wrote + len(data)
                f.write(data)
        if total_size != 0 and wrote != total_size:
            logging.error("ERROR, something went wrong")




def parse_tsv(data: str):
    """
    Parse .tsv file from string
    :param data: str
    :return: list
    """
    if type(data) == str:
        fstream = StringIO(data)
    else:
        raise TypeError("Type of 'data' must be str or bytes.")

    return list(csv.reader(fstream, delimiter="\t"))



def request(url: str, encoding="utf-8"):
    logging.info(f"Requesting Url {url}")
    response = requests.get(url=url)
    logging.info(f"Request finished with status code {response.status_code}")
    response.raise_for_status()
    content = response.content

    if type(content) == bytes:
        return content.decode(encoding)
    else:
        return content


class ColorGradient:
    """
    Create color gradient
    """

    def __init__(self, start: tuple, stop: tuple, steps: int):
        self.start = start
        self.stop = stop
        self.steps = steps


    @staticmethod
    def to_css(color: tuple):
        return "rgb({R},{G},{B})".format(R=color[0], G=color[1], B=color[2])


    def get_list(self):
        return [ColorGradient.list_to_hex(code) for code in ColorGradient._gradient(self.stop, self.start, self.steps)]


    @staticmethod
    def _intermediate(a, b, ratio):

        def _array_multiply(array, c):
            return [element * c for element in array]

        a_component = _array_multiply(a, ratio)
        b_component = _array_multiply(b, 1 - ratio)
        return list(map(sum, zip(a_component, b_component)))


    @staticmethod
    def _gradient(a, b, steps):
        steps -= 1
        steps = [n / float(steps) for n in range(steps)]
        result = [ColorGradient._intermediate(a, b, step) for step in steps]
        result.append(a)
        return result


    @staticmethod
    def list_to_hex(code: list):
        return "#" + "".join(["{:02x}".format(int(num)) for num in code])


    def render_graphviz(self):
        result = self.get_list()
        string = ["digraph G {"]
        for i in range(0, 20):
            # result[i]
            string.append("\tnode[color = \"{COLOR}\" style = filled] {N};".format(COLOR=result[i], N=i))
        string.append("\t" + " -> ".join([str(l) for l in range(0, 20)]))
        string.append("}")
        return "\n".join(string)


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    c = ColorGradient(start=(0, 179, 0), stop=(187, 0, 0), steps=20)
    print(c.get_list())
    print(c.render_graphviz())

    request("http://example.com/")

