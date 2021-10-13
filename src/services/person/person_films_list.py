import json
from functools import lru_cache
from typing import List

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class PersonFilmsListService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_person_films(self, person_id: str) -> List[Film]:
        person_films = await self._get_person_films_from_cache(person_id)
        if not person_films:
            person_films = await self._get_person_films_from_elastic(person_id)
            if not person_films:
                return []
            await self._put_person_films_to_cache(person_films, person_id)
        return person_films

    async def _get_person_films_from_elastic(self, person_id: str) -> List[Film]:
        doc = await self.elastic.get('person', person_id)
        film_ids = doc['_source']['film_ids']
        result = await self.elastic.search(index='film', body={'query': {'terms': {"_id": film_ids}}})
        return [Film(**film['_source']) for film in result['hits']['hits']]

    async def _get_person_films_from_cache(self, person_id: str) -> List[Film]:
        data = await self.redis.get(f'person_films_{person_id}')
        if not data:
            return []

        films = [Film.parse_raw(film) for film in json.loads(data)]
        return films

    async def _put_person_films_to_cache(self, films: List[Film], person_id: str):
        await self.redis.set(f'person_films_{person_id}', json.dumps([film.json() for film in films]),
                             expire=FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_person_films_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonFilmsListService:
    return PersonFilmsListService(redis, elastic)
