""" Pytest fixtures """
# pylint: disable=redefined-outer-name

import os
from typing import Generator

import pytest

from keggtools.storage import Storage
from keggtools.resolver import Resolver



@pytest.fixture(scope="module")
def cachedir() -> str:
    """
    Static cachedir string.
    """

    return os.path.join(os.path.dirname(__file__), ".test_keggtools_cache")



@pytest.fixture(scope="function")
def storage(cachedir: str) -> Generator[Storage, None, None]:
    """
    generate storage instance. Fixtures helps cleanup cache dir after each function call.
    """

    assert os.path.isdir(cachedir) is False

    storage: Storage = Storage(cachedir=cachedir)

    yield storage

    # Cleanup all files in cachedir and remove folder
    for filename in os.listdir(path=cachedir):
        os.remove(path=os.path.join(cachedir, filename))

    os.rmdir(cachedir)

    # try:
    #     # Cleanup all files in cachedir and remove folder
    #     for filename in os.listdir(path=cachedir):
    #         os.remove(path=os.path.join(cachedir, filename))
    #     os.rmdir(cachedir)
    # except OSError:
    #     pass



@pytest.fixture(scope="function")
def resolver(storage: Storage) -> Generator[Resolver, None, None]:
    """
    generate resolver instance on top of storage fixtures.
    """

    test_resolver: Resolver = Resolver(organism="mmu", cache=storage)

    yield test_resolver


