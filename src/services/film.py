from functools import lru_cache
from typing import Optional

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from services.base_services.list_object_service import BaseListService
from pydantic import BaseModel
from models.film import Film
from services.base_services.single_object_service import SingleObjectService


class FilmsListService(BaseListService):

    @staticmethod
    def get_elastic_query(genre: Optional[str], sort: Optional[str]) -> dict:
        query = {
            "sort":
                {sort[1:]: {"order": "desc"}} if sort[0] == '-' else {sort: {"order": "asc"}}
        }
        if genre:
            query["query"] = {"bool": {
                "must":
                    {
                        "nested": {
                            "path": "genres",
                            "query": {
                                "bool": {
                                    "should":
                                        {"term": {"genres.id": genre}}
                                }
                            }
                        }
                    }
            }
            }
        return query


class FilmSearchService(BaseListService):

    @staticmethod
    def get_elastic_query(query: str) -> dict:
        query = {"query": {
            "multi_match": {
                "query": query,
                "fields": ["title", "description"]
            }
        }
    }
        return query


@lru_cache()
def get_list_film_service(
        index: str = 'filmwork',
        model: BaseModel = Film,
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmsListService:
    return FilmsListService(redis, elastic, index, model)


@lru_cache()
def get_search_list_persons_service(
        index: str = 'filmwork',
        model: BaseModel = Film,
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmSearchService:
    return FilmSearchService(redis, elastic, index, model)


@lru_cache()
def get_retrieve_film_service(
        index: str = 'filmwork',
        model: BaseModel = Film,
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> SingleObjectService:
    return SingleObjectService(redis, elastic, index, model)
