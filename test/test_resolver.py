""" Testing keggtools resolver module """

import os
from typing import Dict

import responses

from keggtools import Resolver, Storage, Pathway


from .fixtures import ( # pylint: disable=unused-import
    storage,
    resolver,
    CACHEDIR,
    ORGANISM,
)



def test_resolver_init(storage: Storage) -> None:
    """
    Testing init function of resolver with different arugment types.
    """

    # pylint: disable=redefined-outer-name

    assert Resolver(cache=None).storage.cachedir == Storage().cachedir

    assert Resolver(cache=storage).storage.cachedir == CACHEDIR

    assert Resolver(cache=CACHEDIR).storage.cachedir == CACHEDIR



@responses.activate
def test_resolver_cache_or_request(
    resolver: Resolver, # pylint: disable=redefined-outer-name
    ) -> None:
    """
    Testing resolve cache or request function.
    """

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



@responses.activate
def test_get_pathway_list(
    resolver: Resolver, # pylint: disable=redefined-outer-name
    ) -> None:
    """
    Testing request of pathway list.
    """


    # Register response
    responses.add(
        responses.GET,
        url="http://rest.kegg.jp/list/pathway/mmu",
        body="""path:mmu00010\tGlycolysis / Gluconeogenesis - Mus musculus (house mouse)\n""" \
            """path:mmu00020\tCitrate cycle (TCA cycle) - Mus musculus (house mouse)""",
        status=200,
    )

    result: Dict[str, str] = resolver.get_pathway_list(organism=ORGANISM)

    assert result["path:mmu00010"] == "Glycolysis / Gluconeogenesis - Mus musculus (house mouse)"
    assert result["path:mmu00020"] == "Citrate cycle (TCA cycle) - Mus musculus (house mouse)"



@responses.activate
def test_get_pathway(
    resolver: Resolver, # pylint: disable=redefined-outer-name
    ) -> None:
    """
    Testing request of KGML pathway.
    """

    # Register response
    with open(os.path.join(os.path.dirname(__file__), "pathway.kgml"), "r", encoding="utf-8") as file_obj:
        response_content: str = file_obj.read()

    responses.add(
        responses.GET,
        url="http://rest.kegg.jp/get/mmu12345/kgml",
        body=response_content,
        status=200,
    )

    assert isinstance(resolver.get_pathway(organism=ORGANISM, code="12345"), Pathway) is True


@responses.activate
def test_get_organism_list(
    resolver: Resolver, # pylint: disable=redefined-outer-name
    ) -> None:
    """
    Testing request of org list.
    """

    # Register response
    responses.add(
        responses.GET,
        url="http://rest.kegg.jp/list/organism",
        body="""T01001\thsa\tHomo sapiens (human)\tEukaryotes;Animals;Vertebrates;Mammals\n""" \
            """T01005\tptr\tPan troglodytes (chimpanzee)\tEukaryotes;Animals;Vertebrates;Mammals\n""" \
            """T02283\tpps\tPan paniscus (bonobo)\tEukaryotes;Animals;Vertebrates;Mammals\n""",
        status=200,
    )


    result: Dict[str, str] = resolver.get_organism_list()

    # Check if parsing works
    assert "hsa" in result
    assert result["hsa"] == "Homo sapiens (human)"

    # Testing check organism function
    assert resolver.check_organism(organism="hsa") is True


@responses.activate
def test_get_compounds(
    resolver: Resolver, # pylint: disable=redefined-outer-name
    ) -> None:
    """
    Testing get compund function.
    """

    # Register response
    responses.add(
        responses.GET,
        url="http://rest.kegg.jp/list/compound/",
        body="""cpd:C00001\tH2O; Water\ncpd:C00002\tATP; Adenosine 5'-triphosphate\n""" \
            """cpd:C00003\tNAD+; NAD; Nicotinamide adenine dinucleotide; DPN;\n""" \
            """cpd:C00004\tNADH; DPNH; Reduced nicotinamide adenine dinucleotide\n""" \
            """cpd:C00007\tOxygen; O2\n""",
        status=200,
    )

    result: Dict[str, str] = resolver.get_compounds()

    assert result["cpd:C00007"] == "Oxygen; O2"
