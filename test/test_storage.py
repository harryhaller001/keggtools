""" Testing storage module """

import os

from keggtools.storage import Storage

def test_storage() -> None:
    """
    Testing storage
    """

    storage: Storage = Storage()

    # check if directory exist
    assert os.path.isdir(storage.cachedir) is True

    # Function raises error if dir does not exist
    storage.check_cache_dir()


