from functools import lru_cache

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre
from services.base_services.list_object_service import BaseListService
from services.base_services.single_object_service import SingleObjectService
from db.redis import RedisAdapter
from db.elastic import ElasticAdapter

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


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
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenresListService:
    index = 'genre'
    model = Genre
    cache_adapter = RedisAdapter(redis_instance=redis, model=model, index=index)
    db_adapter = ElasticAdapter(elastic=elastic, model=model, index=index)
    return GenresListService(cache_adapter=cache_adapter, db_adapter=db_adapter)


@lru_cache()
def get_genre_retrieve_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> SingleObjectService:
    index = 'genre'
    model = Genre
    cache_adapter = RedisAdapter(redis_instance=redis, model=model, index=index)
    db_adapter = ElasticAdapter(elastic=elastic, model=model, index=index)
    return SingleObjectService(cache_adapter=cache_adapter, db_adapter=db_adapter)
