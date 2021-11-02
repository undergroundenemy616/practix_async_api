import logging
from functools import lru_cache

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
        doc = await self.db_adapter.get_object_from_db('person', Person, kwargs.pop('person_id'))
        kwargs['film_ids'] = doc.film_ids
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
        redis: RedisAdapter = Depends(get_redis),
        elastic: ElasticAdapter = Depends(get_elastic),
) -> PersonFilmsListService:
    return PersonFilmsListService(cache_adapter=redis, db_adapter=elastic, index='filmwork', model=Film)


@lru_cache()
def get_search_list_persons_service(
        redis: RedisAdapter = Depends(get_redis),
        elastic: ElasticAdapter = Depends(get_elastic),
) -> PersonSearchListService:
    return PersonSearchListService(cache_adapter=redis, db_adapter=elastic, index='person', model=Person)


@lru_cache()
def get_retrieve_person_service(
        redis: RedisAdapter = Depends(get_redis),
        elastic: ElasticAdapter = Depends(get_elastic),
) -> SingleObjectService:
    return SingleObjectService(cache_adapter=redis, db_adapter=elastic, index='person', model=Person)
