import json
from abc import abstractmethod
from typing import List, Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class BaseListFilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    @staticmethod
    @abstractmethod
    def get_films_query(**kwargs):
        pass

    async def get_films(self,
                        page_size: int = 100,
                        page_number: int = 0,
                        **kwargs) -> List[Film]:
        query = self.get_films_query(**kwargs)
        films = await self._get_films_from_cache(query, page_size, page_number)
        if not films:
            films = await self._get_films_from_elastic(query, page_size, page_number)
            if not films:
                return []
            await self._put_films_to_cache(films, query, page_size, page_number)
        return films

    async def _get_films_from_elastic(self, query: dict, page_size: int, page_number: int) -> List[Film]:
        from_ = page_size * (page_number - 1)
        data = await self.elastic.search(index='filmwork',
                                         body=query,
                                         size=page_size,
                                         from_=from_)
        hits = data['hits']['hits']
        return [Film(**film['_source']) for film in hits]

    async def _get_films_from_cache(self, query: dict, page_size: int,
                                    page_number: int) -> Optional[List[Film]]:
        data = await self.redis.get(json.dumps({"index": "filmwork",
                                                "query": query,
                                                "page_size": page_size,
                                                "page_number": page_number}))
        if not data:
            return
        return [Film.parse_raw(film) for film in json.loads(data)]

    async def _put_films_to_cache(self, films_response: List[Film], query: dict, page_size: int,
                                  page_number: int):
        await self.redis.set(json.dumps({"index": "filmwork",
                                         "query": query,
                                         "page_size": page_size,
                                         "page_number": page_number}),
                             json.dumps([film.json() for film in films_response]),
                             expire=FILM_CACHE_EXPIRE_IN_SECONDS)