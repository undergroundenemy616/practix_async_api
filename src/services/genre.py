from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from functools import lru_cache

from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre
from services.base_services.list_object_service import BaseListService
from pydantic import BaseModel

from services.base_services.single_object_service import SingleObjectService

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class GenresListService(BaseListService):

    @staticmethod
    def get_elastic_query(size: int):
        query = {"query": {
            "match_all": {}
            },
            "size": size
        }
        return query


@lru_cache()
def get_genre_list_service(
        index: str = 'genre',
        model: BaseModel = Genre,
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenresListService:
    return GenresListService(redis, elastic, index, model)


@lru_cache()
def get_genre_retrieve_service(
        index: str = 'genre',
        model: BaseModel = Genre,
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> SingleObjectService:
    return SingleObjectService(redis, elastic, index, model)
