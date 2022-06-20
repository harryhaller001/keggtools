""" Testing storage module """

import os

from keggtools.storage import KEGGDataStorage

def test_storage() -> None:
    """
    Testing storage
    """

    storage: KEGGDataStorage = KEGGDataStorage()

    # check if directory exist
    assert os.path.isdir(storage.cachedir) is True

    # Function raises error if dir does not exist
    storage.check_cache_dir()


