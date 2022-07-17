""" Testing storage module """

import os

import pytest

from keggtools.storage import Storage


# TODO: write storage + filename fixtures


def test_storage() -> None:
    """
    Testing storage
    """

    storage: Storage = Storage()

    # check if directory exist
    assert os.path.isdir(storage.cachedir) is True

    # Function raises error if dir does not exist
    storage.check_cache_dir()



def test_folder_generation() -> None:
    """
    Testing generation of new cache folder.
    """

    # Build string of testing cache folder
    cachedir: str = os.path.join(os.path.dirname(__file__), ".test_keggtools_cache")

    assert not os.path.isdir(cachedir)

    storage: Storage = Storage(cachedir=cachedir)

    # Test dir exist
    storage.check_cache_dir()

    # Test correct folder generation
    assert storage.build_cache_path("test.txt") == os.path.join(cachedir, "test.txt")

    # Cleanup. Remove dir
    os.rmdir(cachedir)



def test_folder_check_fails() -> None:
    """
    Testing if check fails if cache folder does not exist.
    """

    # Check error, if folder does not exist

    cachedir: str = os.path.join(os.path.dirname(__file__), ".test_keggtools_cache")
    storage: Storage = Storage(cachedir=cachedir)

    # Remove dir before accessing is
    os.rmdir(cachedir)

    with pytest.raises(NotADirectoryError):
        storage.check_cache_dir()



def test_cache_readwrite() -> None:
    """
    Testing saving/loading of file to storage.
    """

    cachedir: str = os.path.join(os.path.dirname(__file__), ".test_keggtools_cache")
    storage: Storage = Storage(cachedir=cachedir)

    testing_filename: str = "test.txt"
    testing_payload: str = "hello world!"

    # Testing string file
    assert storage.exist(testing_filename) is False
    assert storage.save(filename=testing_filename, data=testing_payload) == os.path.join(cachedir, testing_filename)
    assert storage.load(filename=testing_filename) == testing_payload

    # testing binary file
    assert storage.save_dump(filename=testing_filename, data=testing_payload) == os.path.join(cachedir, testing_filename)
    assert storage.load_dump(filename=testing_filename) == testing_payload


    # Testing loading of none existing files

    with pytest.raises(FileNotFoundError):
        storage.load("invalid.txt")

    with pytest.raises(FileNotFoundError):
        storage.load_dump("invalid.txt")


    # Cleanup
    os.remove(storage.build_cache_path(testing_filename))
    os.rmdir(cachedir)

