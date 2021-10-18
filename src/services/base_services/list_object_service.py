import json
from abc import abstractmethod
from typing import List, Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch

from utils import CACHE_EXPIRE_IN_SECONDS


class BaseListService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, index: str, model):
        self.redis = redis
        self.elastic = elastic
        self.index = index
        self.model = model

    @staticmethod
    @abstractmethod
    def get_elastic_query(**kwargs):
        pass

    async def get_objects(self,
                          page_size: int = 100,
                          page_number: int = 0,
                          **kwargs) -> List:
        query = self.get_elastic_query(**kwargs)
        objects = await self._get_objects_from_cache(query, page_size, page_number)
        if not objects:
            objects = await self._get_objects_from_elastic(query, page_size, page_number)
            if not objects:
                return []
            await self._put_objects_to_cache(objects, query, page_size, page_number)
        return objects

    async def _get_objects_from_elastic(self, query: dict, page_size: int, page_number: int) -> List:
        from_ = page_size * (page_number - 1)
        data = await self.elastic.search(index=self.index,
                                         body=query,
                                         size=page_size,
                                         from_=from_)

        hits = data['hits']['hits']
        return [self.model(**document['_source']) for document in hits]

    async def _get_objects_from_cache(self, query: dict, page_size: int,
                                      page_number: int) -> Optional[List]:

        data = await self.redis.get(json.dumps({"index": self.index,
                                                "query": query,
                                                "page_size": page_size,
                                                "page_number": page_number}))
        if not data:
            return
        return [self.model.parse_raw(document) for document in json.loads(data)]

    async def _put_objects_to_cache(self, objects: List, query: dict, page_size: int,
                                    page_number: int):
        await self.redis.set(json.dumps({"index": self.index,
                                         "query": query,
                                         "page_size": page_size,
                                         "page_number": page_number}),
                             json.dumps([document.json() for document in objects]),
                             expire=CACHE_EXPIRE_IN_SECONDS)
