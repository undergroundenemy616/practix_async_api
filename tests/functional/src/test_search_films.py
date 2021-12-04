import json
from http import HTTPStatus

import pytest
from testdata.filmwork import INDEX_FILM_BODY, INDEX_FILM_NAME, TEST_DATA

from utils.utils import get_expected_hash

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope='module')
async def set_films_test_data(es_client):
    await es_client.indices.create(index=INDEX_FILM_NAME,
                                   body=INDEX_FILM_BODY,
                                   ignore=400)
    result = await es_client.bulk(body=TEST_DATA)
    return result['errors'] is False


async def test_search_film(make_get_request, set_films_test_data):
    response = await make_get_request('/api/v1/film/search?query=Enterprise')

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 1
    assert response.body[0]['id'] == '319df05f-c5d9-4389-a84a-a43e695bf002'


async def test_search_films(make_get_request, set_films_test_data):
    response = await make_get_request('/api/v1/film/search?query=star')

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 3
    assert set(film['title'] for film in response.body) - {'Dark Star', 'Bright Star', 'Rock Star'} == set()

    def check_structure(one_object_structure: dict):
        return set(one_object_structure.keys()) - {'id', 'title', 'rating'} == set()

    assert all(check_structure(obj) for obj in response.body)


async def test_search_films_with_size(make_get_request, set_films_test_data):
    response = await make_get_request('/api/v1/film/search?query=star&page_size=2')

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 2


async def test_search_films_cache(make_get_request, set_films_test_data, redis_client):
    response = await make_get_request('/api/v1/film/search?query=star&page_size=2')

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 2

    elasticsearch_query = {'query': {
        'multi_match': {
            'query': 'star',
            'fields': ['title', 'description']
        }
    }
    }
    key_for_redis = get_expected_hash('filmwork', elasticsearch_query, 2, 1)

    cached_data = await redis_client.get(key_for_redis)
    cached_data = json.loads(cached_data)

    assert len(cached_data) == 2
    assert set(film['title'] for film in response.body) - set(json.loads(film)['title'] for film in cached_data) == set()


async def test_search_films_not_found(make_get_request, set_films_test_data):
    response = await make_get_request('/api/v1/film/search?query=hello')

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 0
