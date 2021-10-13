import json
from functools import lru_cache
from typing import List

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class GenresListService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_genres(self, size: int = 100) -> List[Genre]:
        genres = await self._genres_from_cache()
        if not genres:
            genres = await self._get_genres_from_elastic()
            if not genres:
                return []
            await self._put_genres_to_cache(genres)
        return genres[:size]

    async def _get_genres_from_elastic(self) -> List[Genre]:
        count = await self.elastic.count(index='genre', body={'query': {'match_all': {}}})
        total = count['count']
        result = await self.elastic.search(index='genre', body={'query': {'match_all': {}}}, size=total)
        return [Genre(**genre['_source']) for genre in result['hits']['hits']]

    async def _put_genres_to_cache(self, genres: List[Genre]):
        await self.redis.set('all_genres', json.dumps([genre.json() for genre in genres]),
                             expire=FILM_CACHE_EXPIRE_IN_SECONDS)

    async def _genres_from_cache(self) -> List[Genre]:
        data = await self.redis.get('all_genres')
        if not data:
            return []

        genres = [Genre.parse_raw(genre) for genre in json.loads(data)]
        return genres


@lru_cache()
def get_genre_list_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenresListService:
    return GenresListService(redis, elastic)
