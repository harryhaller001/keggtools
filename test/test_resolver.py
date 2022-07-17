""" Testing keggtools resolver module """

import os

import responses

from keggtools import Resolver


# TODO: fixtures for cache folder

@responses.activate
def test_resolver_cache_or_request() -> None:
    """
    Testing resolve cache or request function.
    """

    cachedir: str = os.path.join(os.path.dirname(__file__), ".test_keggtools_cache")

    resolver: Resolver = Resolver(organism="mmu", cache=cachedir)

    testing_filename: str = "test.txt"
    testing_url: str = "http://example.com/test.txt"
    testing_payload: str = "hello world!"


    # Register response
    responses.add(responses.GET, url=testing_url, body=testing_payload, status=200)

    # File should not exist
    assert resolver.storage.exist(filename=testing_filename) is False

    # Resolver should request the url, because file does not exist

    # pylint: disable=protected-access
    assert resolver._cache_or_request(filename=testing_filename, url=testing_url) == testing_payload

    # File should exist now
    assert resolver.storage.exist(testing_filename) is True


    # Overwrite response with error
    responses.add(responses.GET, url=testing_url, status=400)

    # Resolver should access file from cache
    assert resolver._cache_or_request(filename=testing_filename, url=testing_url) == testing_payload


    # Cleanup
    os.remove(resolver.storage.build_cache_path(testing_filename))
    os.rmdir(cachedir)



def test_get_pathway_list() -> None:
    """
    Testing request of pathway list.
    """

