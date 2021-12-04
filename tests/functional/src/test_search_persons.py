import json
from http import HTTPStatus

import pytest
from testdata.person import INDEX_PERSON_BODY, INDEX_PERSON_NAME, TEST_DATA

from utils.utils import get_expected_hash

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope='module')
async def set_persons_test_data(es_client):
    await es_client.indices.create(index=INDEX_PERSON_NAME,
                                   body=INDEX_PERSON_BODY,
                                   ignore=400)
    result = await es_client.bulk(body=TEST_DATA)
    return result['errors'] is False


async def test_search_person(make_get_request, set_persons_test_data):
    response = await make_get_request('/api/v1/person/search?query=samuel')

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 1
    assert response.body[0]['id'] == '222c4b92-1895-40c7-8b61-98d31b660668'


async def test_search_persons(make_get_request, set_persons_test_data):
    response = await make_get_request('/api/v1/person/search?query=hall')

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 3
    assert set(film['full_name'] for film in response.body) - {'Hall Hood', 'Arsenio Hall', 'Connie Hall'} == set()

    def check_structure(one_object_structure: dict):
        return set(one_object_structure.keys()) - {'id', 'full_name', 'roles', 'film_ids'} == set()

    assert all(check_structure(obj) for obj in response.body)


async def test_search_persons_with_size(make_get_request, set_persons_test_data):
    response = await make_get_request('/api/v1/person/search?query=hall&page_size=2')

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 2


async def test_search_persons_cache(make_get_request, set_persons_test_data, redis_client):
    response = await make_get_request('/api/v1/person/search?query=hall&page_size=2')

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 2

    elasticsearch_query = {'query': {
        'match': {"full_name": 'hall'}
        }
    }
    key_for_redis = get_expected_hash('person', elasticsearch_query, 2, 1)

    cached_data = await redis_client.get(key_for_redis)
    cached_data = json.loads(cached_data)

    assert len(cached_data) == 2
    assert set(person['full_name'] for person in response.body) - set(json.loads(person)['full_name']
                                                                      for person in cached_data) == set()


async def test_search_persons_not_found(make_get_request, set_persons_test_data):
    response = await make_get_request('/api/v1/person/search?query=hello')

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 0
