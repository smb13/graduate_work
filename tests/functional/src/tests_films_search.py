import pytest

from settings import test_settings

pytestmark = [
    pytest.mark.asyncio(),
]


async def test_search_non_existant(make_get_request):
    response = await make_get_request(
        "/api/v1/films/search",
        params={"query": "Abracadabra"},
    )

    assert len(response) == 0


async def test_search_smth_unique(make_get_request):
    response = await make_get_request(
        "/api/v1/films/search",
        params={"query": "Buggles"},
    )

    assert len(response) == 1


async def test_search_empty_query(make_get_request):
    response = await make_get_request(
        "/api/v1/films/search",
        params={"query": "", "page_size": test_settings.page_size_max},
    )

    assert len(response) == test_settings.page_size_max
