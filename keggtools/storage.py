""" Caching """

import logging
import os
import re
import pickle

from .utils import parse_tsv, request as request_url, getcwd
from .const import KEGG_DATA


class KEGGDataStorage:
    """
    Storage Handler
    Dirname of storage saved in variable KEGG_DATA
    """
    @staticmethod
    def _check_env():
        # Check if folder exists
        cache_dir = KEGG_DATA
        if not os.path.isdir(cache_dir):
            logging.debug(f"Cache directory does not exist. Creating directory {cache_dir}")
            os.mkdir(cache_dir)

    @staticmethod
    def build_path(filename: str):
        KEGGDataStorage._check_env()
        return os.path.join(KEGG_DATA, filename)

    @staticmethod
    def exist(filename: str):
        KEGGDataStorage._check_env()
        return os.path.isfile(os.path.join(KEGG_DATA, filename))


    # TODO: remove from storage  --> http request must be performed in resolver
    @staticmethod
    def get_organism_list():
        """
        Get organism codes from file or KEGG API. {<org>: <org-name>}
        :return: dict
        """
        path = KEGGDataStorage.build_path("organism.dump")
        organism_list = {}

        if not os.path.isfile(path):
            # request organism list
            result = parse_tsv(request_url(url="http://rest.kegg.jp/list/organism"))
            for item in result:
                if len(item) == 4 and item[0] != "":
                    organism_list[item[1]] = item[2]
            pickle.dump(organism_list, open(path, "wb"))
            logging.debug("Request organism list and dump to {PATH}".format(PATH=path))
        else:
            organism_list = pickle.load(open(path, "rb"))
            logging.debug("Load organism list from {PATH}".format(PATH=path))
        return organism_list

    @staticmethod
    def get_organism_name(org_code: str):
        """
        Get full name of organism by 3 letter code
        :param org_code: str
        :return: str
        """
        return KEGGDataStorage.get_organism_list().get(org_code, None)

    @staticmethod
    def check_organism(org: str):
        """
        Check if 3 letter organism code exist
        :param org: str
        :return: bool
        """
        organism_list = KEGGDataStorage.get_organism_list()
        return org in organism_list.keys()

    @staticmethod
    def list_existing_pathways():
        """
        List all KEGG pathway files saved in storage directory. [<filename>]
        :return: list
        """
        # <org>_path<code>.kgml
        found = []
        pattern = r"[a-z]{3}_path[0-9]{5}\.kgml"
        for item in os.listdir(KEGG_DATA):
            if re.match(pattern, item, re.IGNORECASE):
                found.append(item)
        logging.debug("Found {N} pathway files".format(N=len(found)))
        return found

    @staticmethod
    def pathway_file_to_id(pathway: str):
        """
        Convert pathway filename to pathway kegg-id
        :param pathway: str
        :return: str
        """
        pattern = r"[a-z]{3}_path([0-9]{5})\.kgml"
        return re.findall(pattern, pathway, re.IGNORECASE)[0]

    @staticmethod
    def pathway_to_id(pathway: str):
        """
        Extract id from pathway kegg-id
        :param pathway: str
        :return: str
        """
        pattern = r"path:[a-z]{3}([0-9]{5})"
        return re.findall(pattern, pathway, re.IGNORECASE)[0]

    @staticmethod
    def pathway_file_exist(org: str, code: str):
        """
        Check if pathway file exist in local storage
        :param org: str
        :param code: str
        :return: bool
        """
        return os.path.isfile(os.path.join(KEGG_DATA, "{ORG}_path{CODE}.kgml".format(ORG=org, CODE=code)))

    @staticmethod
    def pathway_list_exist(org: str):
        """
        Check if list of pathways exists in local stoarage
        :param org: str
        :return bool
        """
        return os.path.isfile(os.path.join(KEGG_DATA, "pathway_{ORG}.dump".format(ORG=org)))

    @staticmethod
    def load_pathway(org: str, code: str):
        """
        Load pathway string from local storage.
        :param org: str
        :param code: str
        :return: str
        """
        if KEGGDataStorage.pathway_file_exist(org=org, code=code):
            return KEGGDataStorage.load("{ORG}_path{CODE}.kgml".format(ORG=org, CODE=code))
        else:
            raise FileNotFoundError("Pathway path:{ORG}{CODE} not saved in local storage".format(ORG=org, CODE=code))

    @staticmethod
    def save(filename: str, data: str):
        """
        Save string as file in local storage. Return path.
        :param filename: str
        :param data: str
        :return: str
        """
        KEGGDataStorage._check_env()
        path = os.path.join(KEGG_DATA, filename)
        with open(path, "w") as f:
            f.write(data)
            f.close()
        return path

    @staticmethod
    def save_dump(filename: str, data):
        """
        Save binary dump as file in local storage. return path.
        :param filename: str
        :param data: str
        :return: str
        """
        KEGGDataStorage._check_env()
        path = os.path.join(KEGG_DATA, filename)
        pickle.dump(data, open(path, "wb"))
        return path

    @staticmethod
    def load(filename: str):
        """
        Load string from file.
        :param filename: str
        :return: str
        """
        KEGGDataStorage._check_env()
        path = os.path.join(KEGG_DATA, filename)
        if not os.path.isfile(path):
            raise FileNotFoundError("File at path {PATH} does not exist".format(PATH=path))
        with open(path, "r") as f:
            data = f.read()
            f.close()
        return data

    @staticmethod
    def load_dump(filename: str):
        """
        Load binary dump from file
        :param filename: str
        :return: object
        """
        KEGGDataStorage._check_env()
        path = os.path.join(KEGG_DATA, filename)
        if not os.path.isfile(path):
            raise FileNotFoundError("File at path {PATH} does not exist".format(PATH=path))
        return pickle.load(open(path, "rb"))


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    # get all stored pathways files from folder
    pathway_files = KEGGDataStorage.list_existing_pathways()
    logging.debug("Found {N} kgml files in folder".format(N=len(pathway_files)))

    # convert pathway file string to pathway ids
    pathway_ids = [KEGGDataStorage.pathway_file_to_id(p) for p in pathway_files]
    logging.debug(len(pathway_ids), "total pathway ids found.")

    # load organism list
    logging.debug(len(KEGGDataStorage.get_organism_list().keys()), "organisms found.")

    # check if pathway file exists
    logging.debug(KEGGDataStorage.pathway_file_exist(org="mmu", code="00010"))

    # check if organism 3 letter code exists
    logging.debug(KEGGDataStorage.check_organism("mmu"))

    # get name of organism from code
    logging.debug(KEGGDataStorage.get_organism_name(org_code="mmu"))

