"""Pytest fixtures."""

import os
from typing import Generator

import pytest

from keggtools.models import Pathway
from keggtools.resolver import Resolver
from keggtools.storage import Storage

# Const values
ORGANISM: str = "mmu"
CACHEDIR: str = os.path.join(os.path.dirname(__file__), ".test_keggtools_cache")


@pytest.fixture(scope="function")
def storage() -> Generator[Storage, None, None]:
    """Generate storage instance. Fixtures helps cleanup cache dir after each function call."""
    assert os.path.isdir(CACHEDIR) is False

    test_storage: Storage = Storage(cachedir=CACHEDIR)

    yield test_storage

    # Cleanup all files in cachedir and remove folder
    for filename in os.listdir(path=CACHEDIR):
        os.remove(path=os.path.join(CACHEDIR, filename))

    # Remove cache dir folder
    os.rmdir(CACHEDIR)


@pytest.fixture(scope="function")
def resolver(
    storage: Storage,
) -> Generator[Resolver, None, None]:
    """Generate resolver instance on top of storage fixtures. `@responses.activate` decorator must be placed at testing methods."""
    test_resolver: Resolver = Resolver(cache=storage)

    yield test_resolver


@pytest.fixture(scope="function")
def pathway() -> Pathway:
    """Return loaded and parsed pathway instance."""
    with open(
        os.path.join(os.path.dirname(__file__), "pathway.kgml"), encoding="utf-8"
    ) as file_obj:
        loaded_pathway: Pathway = Pathway.parse(file_obj.read())

    return loaded_pathway
