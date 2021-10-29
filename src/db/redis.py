import json
from typing import Optional, Any
from abc import abstractmethod

import backoff as backoff
from aioredis import ConnectionClosedError

from aioredis import Redis

from utils import CACHE_EXPIRE_IN_SECONDS


redis: Optional[Redis] = None


# Функция понадобится при внедрении зависимостей
async def get_redis() -> Redis:
    return redis


class AbstractCacheAdapter:

    @abstractmethod
    async def get_objects_from_cache(self, *args):
        pass

    @abstractmethod
    async def put_objects_to_cache(self, *args):
        pass

    @abstractmethod
    async def object_from_cache(self, *args):
        pass

    @abstractmethod
    async def put_object_to_cache(self, *args):
        pass


class RedisAdapter(AbstractCacheAdapter):
    def __init__(self, redis_instance: Redis, model: Any, index: str):
        self.redis = redis_instance
        self.model = model
        self.index = index

    @backoff.on_exception(backoff.expo, ConnectionClosedError)
    async def get_objects_from_cache(self, query: dict, page_size: int,
                                      page_number: int) -> Optional[list]:

        data = await self.redis.get(json.dumps({'index': self.index,
                                                'query': query,
                                                'page_size': page_size,
                                                'page_number': page_number}))
        if not data:
            return
        return [self.model.parse_raw(document) for document in json.loads(data)]

    @backoff.on_exception(backoff.expo, ConnectionClosedError)
    async def put_objects_to_cache(self, objects: list, query: dict, page_size: int,
                                    page_number: int):
        await self.redis.set(json.dumps({'index': self.index,
                                         'query': query,
                                         'page_size': page_size,
                                         'page_number': page_number}),
                             json.dumps([document.json() for document in objects]),
                             expire=CACHE_EXPIRE_IN_SECONDS)

    @backoff.on_exception(backoff.expo, ConnectionClosedError)
    async def object_from_cache(self, object_id: str):
        data = await self.redis.get(object_id)
        if not data:
            return None
        object_ = self.model.parse_raw(data)
        return object_

    @backoff.on_exception(backoff.expo, ConnectionClosedError)
    async def put_object_to_cache(self, object_):
        await self.redis.set(str(object_.id), object_.json(), expire=CACHE_EXPIRE_IN_SECONDS)
