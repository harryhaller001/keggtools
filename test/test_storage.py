""" Testing storage module """
# pylint: disable=unused-import,redefined-outer-name

import os

import pytest

from keggtools.storage import Storage

from .fixtures import cachedir, storage, resolver


def test_storage(cachedir: str) -> None:
    """
    Testing storage.
    """
    assert os.path.isdir(cachedir) is False

    storage: Storage = Storage(cachedir=cachedir)

    # check if directory exist
    assert os.path.isdir(storage.cachedir) is True

    # Function raises error if dir does not exist
    storage.check_cache_dir()

    # Cleanup
    os.rmdir(cachedir)


def test_cachedir_default() -> None:
    """
    Testing storage cachedir default fallback.
    """

    test_storage: Storage = Storage()
    assert os.path.isdir(test_storage.cachedir) is True



def test_folder_generation(cachedir: str, storage: Storage) -> None:
    """
    Testing generation of new cache folder.
    """

    # Test dir exist
    storage.check_cache_dir()

    # Test correct folder generation
    assert storage.build_cache_path("test.txt") == os.path.join(cachedir, "test.txt")



def test_folder_check_fails(cachedir: str, storage: Storage) -> None:
    """
    Testing if check fails if cache folder does not exist.
    """

    # Remove dir before accessing it with storage
    os.rmdir(cachedir)

    with pytest.raises(NotADirectoryError):
        storage.check_cache_dir()


    # Regenerate folder to revent failing of fixture
    os.mkdir(cachedir)



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
    assert storage.save_dump(
        filename=testing_filename,
        data=testing_payload
    ) == os.path.join(cachedir, testing_filename)
    assert storage.load_dump(filename=testing_filename) == testing_payload


    # Testing loading of none existing files

    with pytest.raises(FileNotFoundError):
        storage.load("invalid.txt")

    with pytest.raises(FileNotFoundError):
        storage.load_dump("invalid.txt")


    # Cleanup
    os.remove(storage.build_cache_path(testing_filename))
    os.rmdir(cachedir)
