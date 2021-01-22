
from tqdm import tqdm
import requests
import math
import os
from datetime import datetime


ENSEMBLE_ID_TO_GENE_ID = "_dbOrg_Ensembl_Gene_ID__to__Gene_ID_10090.dump"
GENE_ID_TO_GENE_SYMBOL = "_dbOrg_Gene_ID__to__Gene_Symbol_10090.dump"


def getcwd():
    return os.path.split(__file__)[0]


def get_timestamp():
    return datetime.now().timestamp()


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


class Downloader:
    def __init__(self, url: str):
        self.url = url
        self.output = None

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
            for data in tqdm(r.iter_content(block_size), total=math.ceil(total_size // block_size), unit='KB',
                             unit_scale=True):
                wrote = wrote + len(data)
                f.write(data)
        if total_size != 0 and wrote != total_size:
            print("ERROR, something went wrong")


class Parser:
    @staticmethod
    def parse_tsv(data: str):
        return [tuple(line.strip().split("\t")) for line in data.split("\n")]


class Converter:
    def __init__(self):
        self.ensemble_to_geneid_dict = {}
        self.geneid_to_symbol_dict = {}
        self._load_data()

    def list_convert(self, items: list, convert_function):
        result = []
        for i in items:
            convert = convert_function(i)
            if convert:
                result.append(convert)
        return result

    @staticmethod
    def reverse_dict(data: dict):
        return dict(zip(data.items(), data.keys()))

    def _load_data(self):
        # load dict: ensemble > geneid
        path = os.path.join(getcwd(), ENSEMBLE_ID_TO_GENE_ID)
        for line in open(path, "r").readlines():
            key, val = line.strip().split("\t")
            if key != "" and val != "" and val != "-":
                if "//" in val:
                    val = val.split("//")[0]
                self.ensemble_to_geneid_dict[str(key)] = val

        # load dict: geneid > genesymbol
        path = os.path.join(getcwd(), GENE_ID_TO_GENE_SYMBOL)
        for line in open(path, "r").readlines():
            key, val = line.strip().split("\t")
            if key != "" and val != "" and val != "-":
                if "//" in val:
                    val = val.split("//")[0]
                self.geneid_to_symbol_dict[key] = val

    def ensemble_to_geneid(self, ensemble: str):
        return self.ensemble_to_geneid_dict.get(ensemble, None)

    def geneid_to_ensemble(self, geneid):
        rev = Converter.reverse_dict(self.ensemble_to_geneid_dict)
        return rev.get(str(geneid), None)

    def geneid_to_symbol(self, geneid):
        return self.geneid_to_symbol_dict.get(str(geneid), None)

    def symbol_to_geneid(self, symbol: str):
        rev = Converter.reverse_dict(self.geneid_to_symbol_dict)
        return rev.get(symbol, None)


class ColorGradient:
    """
    c = ColorGradient(start=(0, 179, 0), stop=(187, 0, 0), steps=20)
    print(c.get_list())
    print(c.render_graphviz())
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
    def _arrayMultiply(array, c):
        return [element * c for element in array]

    @staticmethod
    def _arraySum(a, b):
        return list(map(sum, zip(a, b)))

    @staticmethod
    def _intermediate(a, b, ratio):
        aComponent = ColorGradient._arrayMultiply(a, ratio)
        bComponent = ColorGradient._arrayMultiply(b, 1 - ratio)
        return ColorGradient._arraySum(aComponent, bComponent)

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
    # down = Downloader(url="http://example.com")
    # down.set_output("test.bin")
    # down.run()
    c = ColorGradient(start=(0, 179, 0), stop=(187, 0, 0), steps=20)
    print(c.get_list())
    print(c.render_graphviz())
    pass

