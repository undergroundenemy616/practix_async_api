import json
from http import HTTPStatus

import pytest

from testdata.person import TEST_DATA, INDEX_PERSON_BODY, INDEX_PERSON_NAME
from testdata.filmwork import TEST_DATA as TEST_DATA_FILMWORK
from testdata.filmwork import INDEX_FILM_BODY, INDEX_FILM_NAME


pytestmark = pytest.mark.asyncio


@pytest.fixture(scope='module')
async def set_person_test_data(es_client):
    await es_client.indices.create(index=INDEX_PERSON_NAME,
                                   body=INDEX_PERSON_BODY,
                                   ignore=400)
    result = await es_client.bulk(body=TEST_DATA)
    return result['errors'] is False


@pytest.fixture(scope='module')
async def set_films_test_data(es_client):
    await es_client.indices.create(index=INDEX_FILM_NAME,
                                   body=INDEX_FILM_BODY,
                                   ignore=400)
    result = await es_client.bulk(body=TEST_DATA_FILMWORK)
    return result['errors'] is False


async def test_get_person(make_get_request, set_person_test_data):
    test_data_person = TEST_DATA[1]
    lookup_person_id = test_data_person['id']

    response = await make_get_request(f"/api/v1/person/{lookup_person_id}")

    assert response.status == HTTPStatus.OK
    assert response.body['id'] == test_data_person['id']
    assert response.body['full_name'] == test_data_person['full_name']


@pytest.mark.asyncio
async def test_get_person_unknown_id(make_get_request):
    response_not_found = await make_get_request('/api/v1/person/319df05f-c5d9-4389-a84a-a43e695bf444')

    assert response_not_found.status == HTTPStatus.NOT_FOUND
    assert 'detail' in response_not_found.body


@pytest.mark.asyncio
async def test_person_cache(make_get_request, set_person_test_data, redis_client):
    test_data_person = TEST_DATA[1]
    lookup_person_id = test_data_person['id']
    response = await make_get_request(f'/api/v1/person/{lookup_person_id}')

    assert response.status == HTTPStatus.OK

    data = await redis_client.get(test_data_person['id'])
    cached_data = json.loads(data)

    assert test_data_person['full_name'] == cached_data['full_name']


@pytest.mark.asyncio
async def test_person_with_single_films(make_get_request, set_person_test_data, set_films_test_data):
    test_data_person = TEST_DATA[3]
    lookup_person_id = test_data_person['id']
    person_film_endpoint = f'/api/v1/person/{lookup_person_id}/films'

    response = await make_get_request(person_film_endpoint)

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 1
    assert response.body[0]['id'] == '319df05f-c5d9-4389-a84a-a43e695bf000'
    assert response.body[0]['title'] == 'Bright Star'


@pytest.mark.asyncio
async def test_person_without_films(make_get_request, set_person_test_data):
    test_data_person = TEST_DATA[9]
    lookup_person_id = test_data_person['id']
    person_film_endpoint = f'/api/v1/person/{lookup_person_id}/films'

    response = await make_get_request(person_film_endpoint)

    assert response.status == HTTPStatus.OK
    assert len(response.body) == 0

