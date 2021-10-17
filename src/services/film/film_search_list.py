from functools import lru_cache

from aioredis import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from services.film.base_list_film_service import BaseListFilmService


class FilmSearchService(BaseListFilmService):
    @staticmethod
    def get_films_query(query: str) -> dict:
        query = {"query": {
            "multi_match": {
                "query": query,
                "fields": ["title", "description"]
            }
        }
    }
        return query


@lru_cache()
def get_search_list_persons_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmSearchService:
    return FilmSearchService(redis, elastic)
