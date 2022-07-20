""" Testing storage module """

import os

import pytest

from keggtools.storage import Storage

from .fixtures import cachedir, storage, resolver # pylint: disable=unused-import


def test_storage(
    cachedir: str, # pylint: disable=redefined-outer-name
    ) -> None:
    """
    Testing storage.
    """

    # Check cachedir is not present before storage instance is created
    assert os.path.isdir(cachedir) is False

    storage_instance: Storage = Storage(cachedir=cachedir)

    # check if directory exist
    assert os.path.isdir(storage_instance.cachedir) is True

    # Function raises error if dir does not exist
    storage_instance.check_cache_dir()

    # Cleanup
    os.rmdir(cachedir)


def test_cachedir_default() -> None:
    """
    Testing storage cachedir default fallback.
    """

    storage_instance: Storage = Storage()
    assert os.path.isdir(storage_instance.cachedir) is True



def test_folder_generation( # pylint: disable=redefined-outer-name
    cachedir: str,
    storage: Storage,
    ) -> None:
    """
    Testing generation of new cache folder.
    """

    # Test dir exist
    storage.check_cache_dir()

    # Test correct folder generation
    assert storage.build_cache_path("test.txt") == os.path.join(cachedir, "test.txt")



def test_folder_check_fails( # pylint: disable=redefined-outer-name
    cachedir: str,
    storage: Storage,
    ) -> None:
    """
    Testing if check fails if cache folder does not exist.
    """

    # Remove dir before accessing it with storage
    os.rmdir(cachedir)

    with pytest.raises(NotADirectoryError):
        storage.check_cache_dir()


    # Regenerate folder to revent failing of fixture
    os.mkdir(cachedir)



def test_cache_readwrite( # pylint: disable=redefined-outer-name
    cachedir: str,
    storage: Storage,
    ) -> None:
    """
    Testing saving/loading of file to storage.
    """

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
