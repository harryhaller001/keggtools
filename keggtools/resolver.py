""" Resolve requests to KEGG data Api """

from typing import Dict, List, Optional, Union
# from warnings import warn

import requests

from .utils import (
    parse_tsv_to_dict,
    # is_valid_gene_name,
)
from .storage import Storage
from .models import Pathway


def _request(url: str) -> str:
    """
    Url request helper function.

    :param str url: Url to request from.
    """

    response = requests.get(url=url)
    response.raise_for_status()
    return response.content.decode(encoding="utf-8")



def get_gene_names(genes: List[str], max_genes: int = 50) -> Dict[str, str]:
    """
    Resolve KEGG gene identifer to name using to KEGG database REST Api.
    Function is implemented outside the resolver instance, because requests are not cached and only gene identifier
    are used.

    :param typing.List[str] genes: List of gene identifer in format "<organism>:<code>"
    :return: Dict of gene idenifier to gene name.
    :rtype: typing.Dict[str, str]
    """

    if len(genes) == 0:
        raise ValueError("No items to request.")

    # Check maximum number of entries requests
    # TODO: build fallback to make multiple requests from long lists (iterate over list chunks)
    if len(genes) > max_genes:
        raise ValueError(f"Too many entries are requested at once ({len(genes)}/50).")

    # TODO check if pattern of identifer is correct
    # for item in genes:
    #     if not is_valid_gene_name(value=item):
    #         raise ValueError(
    #             f"Item '{item}' is not a valid gene identifer." \
    #             "Identifier must be 3 letter organism code with 5 digit KEGG gene id."
    #         )

    # Build query string
    query_string: str = "+".join(genes)

    # Request without cache
    resolve_dict: Dict[str, str] = parse_tsv_to_dict(data=_request(f"http://rest.kegg.jp/list/{query_string}"))

    # Sanitize dict by splitting first entry of gene name
    result_dict: Dict[str, str] = {}

    for key, value in resolve_dict.items():
        result_dict[key] = value.split(", ")[0]


    # Check if all genes are in dict
    # for item in genes:
    #     if item not in result_dict:
    #         warn(
    #             message=f"Gene identifer '{item}' could not be resolved by API request.",
    #             category=UserWarning,
    #         )


    return result_dict


class Resolver:
    """
    KEGG pathway resolver class.
    Request interface for KEGG API endpoint.
    """

    def __init__(
        self,
        cache: Optional[Union[Storage, str]] = None
    ) -> None:
        """
        Init Resolver instance.

        :param typing.Optional[typing.Union[Storage, str]] cache: Directory to use as cache storage or Storage instance.
        """

        # Handle different types of argument for cache

        _store: Optional[Storage] = None

        if isinstance(cache, str):
            _store = Storage(cachedir=cache)

        elif isinstance(cache, Storage):
            _store = cache
        else:
            # Fallback to default storage with hard coded folder name
            _store = Storage()


        # Internal storage instance
        self.storage: Storage = _store


    def _cache_or_request(
        self,
        filename: str,
        url: str,
        ) -> str:
        """
        Load file from cache folder. If file does not exist, request from given url.

        :param str filename: Filename to store in cache folder.
        :param str url: Url to online resource to request if file is not present in cache folder.
        :return: Returns content of file as string.
        :rtype: str
        """

        file_data: Optional[str] = None

        if self.storage.exist(filename=filename):

            # return pathway list dump
            file_data = self.storage.load(filename=filename)

        else:

            # Data not found in cache. Request from REST api

            file_data = _request(url=url)

            # Save in storage
            self.storage.save(filename=filename, data=file_data)

        return file_data




    def get_pathway_list(
        self,
        organism: str,
        ) -> Dict[str, str]:
        """
        Request list of pathways linked to organism.

        :param str organism: 3 letter organism code used by KEGG database.
        :return: Dict in format {<pathway-id>: <name>}.
        :rtype: typing.Dict[str, str]
        """

        # TODO: return as list of pathway identifier ?

        # TODO: verify org code

        # path:mmu00010	Glycolysis / Gluconeogenesis - Mus musculus (mouse)
        # path:<org><code>\t<name> - <org>


        list_data: str = self._cache_or_request(
            filename=f"pathway_list_{organism}.tsv",
            url=f"http://rest.kegg.jp/list/pathway/{organism}"
        )


        pathways: Dict[str, str] = parse_tsv_to_dict(
            data=list_data,
        )

        # return pathway list
        return pathways


    def get_pathway(
        self,
        organism: str,
        code: str,
        ) -> Pathway:
        """
        Load and parse KGML pathway by identifier.

        :param str organism: 3 letter organism code used by KEGG database.
        :param str code: Pathway identify used by KEGG database.
        :return: Returns parsed Pathway instance.
        :rtype: Pathway
        """

        # TODO: verify org code

        data: str = self._cache_or_request(
            filename=f"{organism}_path{code}.kgml",
            url=f"http://rest.kegg.jp/get/{organism}{code}/kgml",
        )

        # Parse string
        return Pathway.parse(data)



    def get_compounds(self) -> Dict[str, str]:
        """
        Get dict of components. Request from KEGG API if not in cache.

        :return: Dict of compound identifier to compound name.
        :rtype: typing.Dict[str, str]
        """

        compound_data: str = self._cache_or_request(
            filename="compound.tsv",
            url="http://rest.kegg.jp/list/compound",
        )

        # Parse tsv string
        result: Dict[str, str] = parse_tsv_to_dict(data=compound_data)

        return result



    def get_organism_list(self) -> Dict[str, str]:
        """
        Get organism codes from file or KEGG API.

        :return: Dict with format {<org>: <org-name>}
        :rtype: typing.Dict[str, str]
        """

        data: str = self._cache_or_request(
            filename="organism.tsv",
            url="http://rest.kegg.jp/list/organism"
        )

        result: Dict[str, str] = parse_tsv_to_dict(
            data=data,
            col_keys=1,
            col_values=2,
        )

        return result


    def check_organism(self, organism: str) -> bool:
        """
        Check if organism code exist.

        :param str organism: 3 letter organism code used by KEGG database.
        :return: Returns True if organism code is found in list of valid organisms.
        :rtype: bool
        """

        organism_list = self.get_organism_list()
        return organism_list.get(organism) is not None
