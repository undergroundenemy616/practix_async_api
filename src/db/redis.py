import json
from abc import abstractmethod
from typing import Any, Optional

import backoff as backoff
from aioredis import ConnectionClosedError, Redis

from utils import CACHE_EXPIRE_IN_SECONDS, get_redis_key_hash

redis: Optional[Redis] = None


class AbstractCacheAdapter:

    @abstractmethod
    async def get_objects_from_cache(self, *args):
        pass

    @abstractmethod
    async def put_objects_to_cache(self, *args):
        pass


class RedisAdapter(AbstractCacheAdapter):
    def __init__(self, redis_instance: Redis):
        self.redis = redis_instance

    @backoff.on_exception(backoff.expo, ConnectionClosedError)
    async def get_objects_from_cache(self, redis_key: str) -> Optional[list]:
        data = await self.redis.get(redis_key)
        if not data:
            return
        return data

    @backoff.on_exception(backoff.expo, ConnectionClosedError)
    async def put_objects_to_cache(self, objects: list or dict, redis_key: str):
        await self.redis.set(redis_key, objects, expire=CACHE_EXPIRE_IN_SECONDS)


async def get_redis() -> RedisAdapter:
    return RedisAdapter(redis_instance=redis)
