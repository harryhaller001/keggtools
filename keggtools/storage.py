""" Storage of KEGG data. Caching downloaded files from API to local file system. """

import os
import pickle
from typing import Any, Optional


class Storage:
    """
    Storage handler class.
    """

    def __init__(self, cachedir: Optional[str] = None) -> None:
        """
        Init KEGG data storage instance.
        :param cachedir: str
        """

        if cachedir is None:
            # Cachedir argument not given. Fallback to default cache directory
            cachedir = os.path.join(os.getcwd(), ".keggtools_cache")


        if os.path.isdir(cachedir) is False:
            # Directory does not exist. Auto-generate diretory
            os.mkdir(cachedir)
            # logging.info("Cache folder '%s' does not exist. Auto-generating folder.", cachedir)
            # raise NotADirectoryError(f"Directory '{cachedir}' does not exist.")


        self.cachedir = cachedir



    def check_cache_dir(self) -> None:
        """
        Checks if cache dir exist. Raises "NotADirectoryError" of caching folder not found.
        """

        if os.path.isdir(self.cachedir) is False:
            raise NotADirectoryError(f"Directory '{self.cachedir}' does not exist.")



    def build_cache_path(self, filename: str) -> str:
        """
        Build absolute filename for caching directory.
        :param filename: str
        :return: str
        """

        self.check_cache_dir()
        return os.path.join(self.cachedir, filename)


    def exist(self, filename: str) -> bool:
        """
        Check if filename exist in caching dir
        :param filename: str
        :return: bool
        """

        self.check_cache_dir()
        return os.path.isfile(os.path.join(self.cachedir, filename))


    def save(self, filename: str, data: str) -> str:
        """
        Save string as file in local storage. Returns absolute filename of save file.
        :param filename: str
        :param data: str
        :return: str
        """

        self.check_cache_dir()
        path: str = self.build_cache_path(filename=filename)

        with open(path, "w", encoding="utf-8") as f_obj:
            f_obj.write(data)
            f_obj.close()

        return path


    def save_dump(self, filename: str, data: Any) -> str:
        """
        Save binary dump as file in local storage. Returns absolute filename of save file.
        :param filename: str
        :param data: Any
        :return: str
        """

        self.check_cache_dir()
        path: str = self.build_cache_path(filename=filename)

        with open(path, "wb") as output_file:
            pickle.dump(data, output_file)

        return path


    def load(self, filename: str) -> str:
        """
        Load string from file.
        :param filename: str
        :return: str
        """

        path: str = self.build_cache_path(filename=filename)

        if not os.path.isfile(path):
            raise FileNotFoundError(f"Can not load file. File at path '{path}' does not exist.")

        with open(path, "r", encoding="utf-8") as f_obj:
            data = f_obj.read()
            f_obj.close()

        return data


    def load_dump(self, filename: str) -> Any:
        """
        Load binary dump from file
        :param filename: str
        :return: object
        """

        path: str = self.build_cache_path(filename=filename)

        if not os.path.isfile(path):
            raise FileNotFoundError(f"Can not load file. File at path '{path}' does not exist.")

        with open(path, "rb") as input_file:
            return pickle.load(input_file)


