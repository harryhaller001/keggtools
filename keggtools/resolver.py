""" Resolve requests to KEGG data Api """

from typing import Dict, Optional, Union

import requests

from .utils import parse_tsv_to_dict
from .storage import Storage
from .models import Pathway


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

        :param Optional[Union[Storage, str]] cache: Directory to use as cache storage or Storage instance.
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

            response = requests.get(url=url)
            response.raise_for_status()
            file_data = response.content.decode(encoding="utf-8")

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
        :rtype: Dict[str, str]
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

        :return: dict
        """

        compound_data: str = self._cache_or_request(
            filename="compound.tsv",
            url="http://rest.kegg.jp/list/compound/",
        )

        # Parse tsv string
        result: Dict[str, str] = parse_tsv_to_dict(data=compound_data)

        return result



    def get_organism_list(self) -> Dict[str, str]:
        """
        Get organism codes from file or KEGG API.

        :return: dict {<org>: <org-name>}
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

        :param organism: (str) 3 letter organism code used by KEGG database.
        :return: (bool) returns True if organism code is found in list of valid organisms.
        """

        organism_list = self.get_organism_list()
        return organism_list.get(organism) is not None
