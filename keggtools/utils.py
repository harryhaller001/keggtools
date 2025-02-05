"""Basic utils for HTTP requests, parsing and rendering."""

import csv
import os
import re
from io import StringIO
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

import pandas as pd

# XML parsing helper functions


def parse_xml(xml_object_or_string: str | Element) -> Element:
    """Returns XML Element object from string or XML Element.

    :param typing.Union[str, xml.etree.ElementTree.Element] xml_object_or_string: Input parameter to check.
    :return: XML element instance.
    :rtype: xml.etree.ElementTree.Element
    """
    if isinstance(xml_object_or_string, str):
        return ElementTree.fromstring(xml_object_or_string)
    return xml_object_or_string


def parse_tsv(data: str) -> list:
    """Parse .tsv file from string.

    :param str data: Tsv string to parse into list.
    :return: List of items.
    :rtype: list
    """
    return list(csv.reader(StringIO(data), delimiter="\t"))


def parse_tsv_to_dict(
    data: str,
    col_keys: int = 0,
    col_values: int = 1,
) -> dict[str, str]:
    """Parse .tsv file from string and build dict from first two columns. Other columns are ignored.

    :param str data: Tsv string to parse.
    :param int col_keys: Number of colum to parse as dict keys (0-index).
    :param int col_values: Number of colum to parse as dict values (0-index).
    :return: Dict of two tsv columns.
    :rtype: typing.Dict[str, str]
    """
    list_data: list = parse_tsv(data=data)

    result: dict[str, str] = {}

    for row in list_data:
        if len(row) >= 2 and row[col_keys] != "":
            result[row[col_keys]] = row[col_values]

        # TODO: handle else cases or ignore silent ?

    return result


class ColorGradient:
    """Create color gradient."""

    def __init__(self, start: tuple, stop: tuple, steps: int = 100) -> None:
        """Init ColorGradient instance.

        :param tuple start: Color tuple
        :param tuple stop: Color tuple
        :param int steps: Number of steps.
        """
        self.start: tuple = start
        self.stop: tuple = stop
        self.steps: int = steps

    @staticmethod
    def to_css(color: tuple) -> str:
        """Convert color tuple to CSS rgb color string.

        :param tuple color: RGB color tuple containing 3 integers
        :return: Color as CSS string (e.g. "rgb(0, 0, 0)").
        :rtype: str
        """
        # if len(color) != 3 or not all([isinstance(value, int) for value in color]):
        #     raise ValueError("Color must be a tuple of 3 integers.")

        return f"rgb({color[0]},{color[1]},{color[2]})".lower()

    @staticmethod
    def to_hex(color: tuple) -> str:
        """Convert color tuple to hex color string.

        :param tuple color: RGB color tuple containing 3 integers.
        :return: Hexadecimal color string (e.g. "#000000").
        :rtype: str
        """
        # TODO: check for int type.
        # TODO: check for 0-255 range

        return f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}".lower()

    def get_list(self) -> list[str]:
        """Get gradient color as list.

        :return: Returns list of hexadecimal color strings with a gradient.
        :rtype: typing.List[str]
        """
        step_list = [index / float(self.steps) for index in range(self.steps)]
        result = [ColorGradient._intermediate(self.stop, self.start, step) for step in step_list]
        result.append(self.stop)

        return [ColorGradient.to_hex(code) for code in result]

    @staticmethod
    def _intermediate(a_var: tuple, b_var: tuple, ratio: float) -> tuple:
        def _array_multiply(array, c_var):
            return [element * c_var for element in array]

        a_component = _array_multiply(a_var, ratio)
        b_component = _array_multiply(b_var, 1 - ratio)
        values: list[float] = list(map(sum, zip(a_component, b_component, strict=False)))

        return tuple(int(item) for item in values)


def is_valid_pathway_org(value: str) -> bool:
    """Check if organism identifier is valid.

    :param str value: String value to check.
    :return: Returns True if value is a valid organism code.
    :rtype: bool
    """
    # Organism must be 3 letter code
    # Identifier can also be KO or Enzyme identifer
    # TODO: validate with KEGG organism list
    return re.match(pattern=r"^(ko|ec|[a-z]{3})$", string=value) is not None


def is_valid_pathway_number(value: str) -> bool:
    """Check if pathway number has correct 5 digit format.

    :param str value: String value to check.
    :return: Returns True if value has the correct format of pathway number.
    :rtype: bool
    """
    # KEGG pathway number must be a 5 digit number
    return re.match(pattern=r"^([0-9]{5})$", string=value) is not None


def is_valid_pathway_name(value: str) -> bool:
    """Check if combined pathway identifer is valid. String must match "path:<org><number>".

    :param str value: String value to check.
    :return: Returns True if value matches format of pathway name.
    :rtype: bool
    """
    return re.match(pattern=r"^path:(ko|ec|[a-z]{3})([0-9]{5})$", string=value) is not None


def is_valid_hex_color(value: str) -> bool:
    """Check if string is a valid hex color.

    :param str value: String value to check.
    :return: Returns True if value is valid hexadecimal color string.
    :rtype: bool
    """
    return re.match(pattern=r"^\#([a-fA-F0-9]{6})$", string=value) is not None


def is_valid_gene_name(value: str) -> bool:
    """Check if gene identifer is valid. String must match "<org>:<number>".

    :param str value: String value to check.
    :return: Returns True if value matches format of gene name.
    :rtype: bool
    """
    # TODO Support ko|ec entries ???
    return re.match(pattern=r"^([a-z]{3}):([0-9]{5})$", string=value) is not None


# TODO: is a custom warning class needed
# class MissingDataWarning(Warning):
#     """
#     Warning to alert user of missing data.
#     """

#     def __init__(self, message: str) -> None:
#         """
#         Init custom missing data warning instance.

#         :param str message: Message of missing data warning.
#         """

#         # Call super init method
#         super().__init__()

#         self.message: str = message


#     def __str__(self) -> str:
#         """
#         Missing data warning instance to string.

#         :return: String of message.
#         :rtype: str
#         """

#         return repr(self.message)


def merge_entrez_geneid(
    diffexp: pd.DataFrame,
    gene_column: str = "names",
    dataset_name: str = "hsapiens_gene_ensembl",
    symbol_source: str = "hgnc_symbol",
    entrez_source: str = "entrezgene_id",
    use_cache: bool = True,
) -> pd.DataFrame:
    """Use pybiomart to merge entrez gene id to differential expression dataframe.

    :param pandas.DataFrame diffexp: Pandas dataframe containing to differential expression data.
    :param str gene_column: Name of column in differential expression dataframe that contains to gene symbol.
    :param str dataset_name: Biomart dataset to use for conversion.
    :param str symbol_source: Biomart source dataset for gene symbol.
    :param str entrez_source: Biomart source dataset for entrez id.
    :param bool use_cache: Use cache for pybioart requests. Defaults to `True`.
    :return: Returns differential expression dataframe with merged column for entrez id.
    :rtype: pandas.DataFrame
    """
    from pybiomart import Dataset

    dataset = Dataset(name=dataset_name, host="http://www.ensembl.org", use_cache=use_cache)
    # Query dataset
    convert_df = dataset.query(attributes=[symbol_source, entrez_source])
    # Rename columns
    convert_df.columns = ["symbol", "entrez"]
    # Remove missing entrez ids
    convert_df = convert_df[~convert_df["entrez"].isna()]

    # Convert entrez id to string type
    convert_df["entrez"] = convert_df["entrez"].astype(int)
    convert_df["entrez"] = convert_df["entrez"].astype(str)

    # merge with diffexp df
    diffexp = diffexp.merge(right=convert_df, how="left", left_on=gene_column, right_on="symbol")
    # Filter missing entrez ids
    diffexp = diffexp[~diffexp["entrez"].isna()]
    return diffexp


def msig_to_kegg_id() -> pd.DataFrame:
    """Load dataframe to map canonical pathway id of MSigDB to KEGG pathway id.

    Returns:
        pandas.DataFrame: Dataframe containing MSigDB id and KEGG pathway id.

    Raises:
        AssertionError: If mapping file does not exist.
    """
    input_filename = os.path.join(os.path.dirname(__file__), "_static", "msig_to_kegg_id.csv")

    assert os.path.isfile(input_filename), "File 'msig_to_kegg_id.csv' is missing."

    return pd.read_csv(input_filename, sep=",")
