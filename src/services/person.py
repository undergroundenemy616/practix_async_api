from functools import lru_cache
from typing import List

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from services.base_services.list_object_service import BaseListService
from pydantic import BaseModel
from models.person import Person
import logging

from services.base_services.single_object_service import SingleObjectService

logging.basicConfig(level=logging.INFO)


FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class PersonFilmsListService(BaseListService):
    @staticmethod
    def get_elastic_query(film_ids: List):
        query = {'query': {
            'terms': {"_id": film_ids}
            }
        }
        logging.info(query)
        return query

    async def get_objects(self,
                          page_size: int = 100,
                          page_number: int = 0,
                          **kwargs) -> List:
        doc = await self.elastic.get('person', kwargs.pop('person_id'))
        kwargs['film_ids'] = doc['_source']['film_ids']
        return await super().get_objects(page_size, page_number, **kwargs)


class PersonSearchListService(BaseListService):

    @staticmethod
    def get_elastic_query(query: List):
        query = {'query': {
            'match': {"full_name": query}
            }
        }
        return query


@lru_cache()
def get_person_films_service(
        index: str = 'person',
        model: BaseModel = Person,
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonFilmsListService:
    return PersonFilmsListService(redis, elastic, index, model)


@lru_cache()
def get_search_list_persons_service(
        index: str = 'person',
        model: BaseModel = Person,
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonSearchListService:
    return PersonSearchListService(redis, elastic, index, model)


@lru_cache()
def get_retrieve_person_service(
        index: str = 'person',
        model: BaseModel = Person,
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> SingleObjectService:
    return SingleObjectService(redis, elastic, index, model)
