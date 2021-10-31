import json
import pytest

from testdata.person import TEST_DATA, INDEX_PERSON_BODY, INDEX_PERSON_NAME


@pytest.fixture(scope='module')
async def set_person_test_data(es_client):
    await es_client.indices.create(index=INDEX_PERSON_NAME,
                                   body=INDEX_PERSON_BODY,
                                   ignore=400)
    result = await es_client.bulk(body=TEST_DATA)
    return result['errors'] is False


@pytest.mark.asyncio
async def test_list_person(make_get_request, set_person_test_data):
    response = await make_get_request('/api/v1/person')

    assert response.status == 200
    assert len(response.body) == 5


@pytest.mark.asyncio
async def test_list_person_with_size(make_get_request, set_person_test_data):
    response = await make_get_request('/api/v1/person?page_size=2')

    assert response.status == 200
    assert len(response.body) == 2


@pytest.mark.asyncio
async def test_retrieve_person(make_get_request, set_person_test_data):
    test_data_person = TEST_DATA[0]
    response = await make_get_request(f"/api/v1/person/{test_data_person['id']}")
    assert response.status == 200
    assert response.body['id'] == test_data_person['id']
    assert response.body['full_name'] == test_data_person['full_name']


@pytest.mark.asyncio
async def test_person_cache(make_get_request, set_person_test_data, redis_client):
    test_data_person = TEST_DATA[0]
    response = await make_get_request(f"/api/v1/person/{test_data_person['id']}")

    assert response.status == 200

    cached_data = await redis_client.get(test_data_person['id'])
    cached_data = json.loads(cached_data)
    assert test_data_person['full_name'] == cached_data['full_name']
