import json
import math
from functools import lru_cache
from typing import Optional, List

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from pydantic import BaseModel, validator, ValidationError

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class PersonListResponse(BaseModel):
    total_pages: int
    page: int
    objects: List[Person] = []

    @validator('page')
    def page_number(cls, value, values):
        if value > values['total_pages']:
            raise ValidationError
        return value


class PersonSearchListService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_search_persons(self, query, page_size: int = 100, page_number: int = 0):
        persons_response = await self._search_persons_from_cache(query, page_size, page_number)
        if not persons_response:
            persons_response = await self._get_search_persons_from_elastic(query, page_size, page_number)
            await self._put_search_persons_to_cache(persons_response, query, page_size, page_number)
        return persons_response

    async def _get_search_persons_from_elastic(self, query: str, page_size: int = 100,
                                               page_number: int = 1) -> PersonListResponse:
        count = await self.elastic.count(index='person',
                                         body={'query': {'match': {"full_name": query}}})
        total = count['count']
        total_pages = int(math.ceil(total / page_size))
        from_ = page_size * (page_number - 1)
        data = await self.elastic.search(index='person',
                                         body={'query': {'match': {"full_name": query}}},
                                         size=page_size,
                                         from_=from_)
        hits = data['hits']['hits']
        return PersonListResponse(total_pages=total_pages,
                                  page=page_number,
                                  objects=[Person(**person['_source']) for person in hits])

    async def _search_persons_from_cache(self, query: str, page_size: int,
                                         page_number: int) -> Optional[PersonListResponse]:
        data = await self.redis.get(json.dumps({"index": "person",
                                                "query": query,
                                                "page_size": page_size,
                                                "page_number": page_number}))
        if not data:
            return
        return PersonListResponse.parse_raw(data)

    async def _put_search_persons_to_cache(self, persons_response: PersonListResponse, query: str, page_size: int,
                                           page_number: int):
        await self.redis.set(json.dumps({"index": "person",
                                         "query": query,
                                         "page_size": page_size,
                                         "page_number": page_number}),
                             persons_response.json(),
                             expire=FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_search_list_persons_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonSearchListService:
    return PersonSearchListService(redis, elastic)
