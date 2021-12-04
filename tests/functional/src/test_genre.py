import json
from http import HTTPStatus

import pytest
from testdata.genre import INDEX_GENRE_BODY, INDEX_GENRE_NAME, TEST_DATA

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope='module')
async def set_genres_test_data(es_client):
    await es_client.indices.create(index=INDEX_GENRE_NAME,
                                   body=INDEX_GENRE_BODY,
                                   ignore=400)
    result = await es_client.bulk(body=TEST_DATA)
    return result['errors'] is False


async def test_list_genre(make_get_request, set_genres_test_data):
    response = await make_get_request('/api/v1/genre')

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 7


async def test_list_genre_with_size(make_get_request, set_genres_test_data):
    response = await make_get_request('/api/v1/genre?page_size=2')

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 2


async def test_retrieve_genre(make_get_request, set_genres_test_data):
    test_data_genre = TEST_DATA[1]

    response = await make_get_request(f"/api/v1/genre/{test_data_genre['id']}")

    assert response.status == HTTPStatus.OK
    assert response.body['id'] == test_data_genre['id']
    assert response.body['name'] == test_data_genre['name']
    assert response.body['description'] == test_data_genre['description']


async def test_genre_cache(make_get_request, set_genres_test_data, redis_client):
    test_data_genre = TEST_DATA[1]

    response = await make_get_request(f"/api/v1/genre/{test_data_genre['id']}")

    assert response.status == HTTPStatus.OK

    cached_data = await redis_client.get(test_data_genre['id'])
    cached_data = json.loads(cached_data)

    assert test_data_genre['name'] == cached_data['name']
    assert test_data_genre['description'] == cached_data['description']
