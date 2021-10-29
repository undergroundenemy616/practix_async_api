import logging
from functools import lru_cache

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic, ElasticAdapter
from db.redis import get_redis, RedisAdapter
from models.film import Film
from models.person import Person
from services.base_services.list_object_service import BaseListService
from services.base_services.single_object_service import SingleObjectService

logging.basicConfig(level=logging.INFO)


class PersonFilmsListService(BaseListService):
    @staticmethod
    def get_elastic_query(film_ids: list):
        query = {'query': {
            'terms': {"_id": film_ids}
            }
        }
        logging.info(query)
        return query

    async def get_objects(self,
                          page_size: int = 100,
                          page_number: int = 0,
                          **kwargs) -> list:
        doc = await self.db_adapter.get('person', kwargs.pop('person_id'))
        kwargs['film_ids'] = doc['_source']['film_ids']
        return await super().get_objects(page_size, page_number, **kwargs)


class PersonSearchListService(BaseListService):

    @staticmethod
    def get_elastic_query(query: list):
        query = {'query': {
            'match': {"full_name": query}
            }
        }
        return query


@lru_cache()
def get_person_films_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonFilmsListService:
    index = 'filmwork'
    model = Film
    cache_adapter = RedisAdapter(redis_instance=redis, model=model, index=index)
    db_adapter = ElasticAdapter(elastic=elastic, model=model, index=index)
    return PersonFilmsListService(cache_adapter=cache_adapter, db_adapter=db_adapter)


@lru_cache()
def get_search_list_persons_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonSearchListService:
    index = 'person'
    model = Person
    cache_adapter = RedisAdapter(redis_instance=redis, model=model, index=index)
    db_adapter = ElasticAdapter(elastic=elastic, model=model, index=index)
    return PersonSearchListService(cache_adapter=cache_adapter, db_adapter=db_adapter)


@lru_cache()
def get_retrieve_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> SingleObjectService:
    index = 'person'
    model = Person
    cache_adapter = RedisAdapter(redis_instance=redis, model=model, index=index)
    db_adapter = ElasticAdapter(elastic=elastic, model=model, index=index)
    return SingleObjectService(cache_adapter=cache_adapter, db_adapter=db_adapter)
