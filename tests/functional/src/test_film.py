import json
import pytest

from ..testdata.filmwork import TEST_DATA, INDEX_FILM_BODY, INDEX_FILM_NAME


@pytest.fixture(scope='module')
async def set_films_test_data(es_client):
    await es_client.indices.create(index=INDEX_FILM_NAME,
                                   body=INDEX_FILM_BODY,
                                   ignore=400)
    result = await es_client.bulk(body=TEST_DATA)
    return result['errors'] is False


@pytest.mark.asyncio
async def test_list_films(make_get_request, set_films_test_data):
    response = await make_get_request('/api/v1/film')

    assert response.status == 200
    assert len(response.body) == 5

@pytest.mark.asyncio
async def test_list_genre_with_size(make_get_request, set_films_test_data):
    response = await make_get_request('/api/v1/film?page_size=2')

    assert response.status == 200
    assert len(response.body) == 2


@pytest.mark.asyncio
async def test_retrieve_film(make_get_request, set_films_test_data):
    test_data_genre = TEST_DATA[0]
    response = await make_get_request(f"/api/v1/genre/{test_data_genre['id']}")
    assert response.status == 200
    assert response.body['id'] == test_data_genre['id']
    assert response.body['type'] == test_data_genre['type']
    assert response.body['title'] == test_data_genre['title']



@pytest.mark.asyncio
async def test_genre_cache(make_get_request, set_films_test_data, redis_client):
    test_data_genre = TEST_DATA[0]
    response = await make_get_request(f"/api/v1/film/{test_data_genre['id']}")

    assert response.status == 200

    cached_data = await redis_client.get(test_data_genre['id'])
    cached_data = json.loads(cached_data)
    assert test_data_genre['type'] == cached_data['type']
    assert test_data_genre['title'] == cached_data['title']
