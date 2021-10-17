from functools import lru_cache
from typing import Optional

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from services.film.base_list_film_service import BaseListFilmService


class FilmsListService(BaseListFilmService):
    @staticmethod
    def get_films_query(genre: Optional[str], sort: Optional[str]) -> dict:
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


@lru_cache()
def get_list_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmsListService:
    return FilmsListService(redis, elastic)
