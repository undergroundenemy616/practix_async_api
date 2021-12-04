from functools import lru_cache

from fastapi import Depends

from db.elastic import ElasticAdapter, get_elastic
from db.redis import RedisAdapter, get_redis
from models.genre import Genre
from services.base_services.list_object_service import BaseListService
from services.base_services.single_object_service import SingleObjectService


class GenresListService(BaseListService):

    @staticmethod
    def get_elastic_query(size: int):
        query = {'query': {
            'match_all': {}
            },
            'size': size
        }
        return query


@lru_cache()
def get_genre_list_service(
        redis: RedisAdapter = Depends(get_redis),
        elastic: ElasticAdapter = Depends(get_elastic),
) -> GenresListService:
    return GenresListService(cache_adapter=redis, db_adapter=elastic, index='genre', model=Genre)


@lru_cache()
def get_genre_retrieve_service(
        redis: RedisAdapter = Depends(get_redis),
        elastic: ElasticAdapter = Depends(get_elastic),
) -> SingleObjectService:
    return SingleObjectService(cache_adapter=redis, db_adapter=elastic, index='genre', model=Genre)
