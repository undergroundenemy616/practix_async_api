import json
from http import HTTPStatus

import pytest

from testdata.filmwork import TEST_DATA, INDEX_FILM_BODY, INDEX_FILM_NAME

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope='module')
async def set_films_test_data(es_client):
    await es_client.indices.create(index=INDEX_FILM_NAME,
                                   body=INDEX_FILM_BODY,
                                   ignore=400)
    result = await es_client.bulk(body=TEST_DATA)
    return result['errors'] is False


async def test_list_films(make_get_request, set_films_test_data):
    response = await make_get_request('/api/v1/film')

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 5


async def test_list_film_with_size(make_get_request, set_films_test_data):
    response = await make_get_request('/api/v1/film?page_size=2')

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 2


async def test_get_film(make_get_request, set_films_test_data):
    test_data_film = TEST_DATA[1]
    response = await make_get_request(f"/api/v1/film/{test_data_film['id']}")
    assert response.status == HTTPStatus.OK
    assert response.body['id'] == test_data_film['id']
    assert response.body['rating'] == test_data_film['rating']
    assert response.body['title'] == test_data_film['title']


@pytest.mark.asyncio
async def test_get_film_unknown_id(make_get_request):
    response_not_found = await make_get_request('/api/v1/film/319df05f-c5d9-4389-a84a-a43e695bf444')

    assert response_not_found.status == HTTPStatus.NOT_FOUND
    assert 'detail' in response_not_found.body


@pytest.mark.asyncio
async def test_get_film_invalid_id(make_get_request):
    response_not_found = await make_get_request('/api/v1/film/10000')

    assert response_not_found.status == HTTPStatus.NOT_FOUND
    assert 'detail' in response_not_found.body


async def test_film_cache(make_get_request, set_films_test_data, redis_client):
    test_data_film = TEST_DATA[1]
    response = await make_get_request(f"/api/v1/film/{test_data_film['id']}")

    assert response.status == HTTPStatus.OK

    data = await redis_client.get(test_data_film['id'])
    cached_data = json.loads(data)
    assert test_data_film['type'] == cached_data['type']
    assert test_data_film['title'] == cached_data['title']
