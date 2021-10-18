from aioredis import Redis
from elasticsearch import AsyncElasticsearch

from utils import CACHE_EXPIRE_IN_SECONDS


class SingleObjectService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, index: str, model):
        self.redis = redis
        self.elastic = elastic
        self.index = index
        self.model = model

    async def get_by_id(self, object_id: str):
        object_ = await self._object_from_cache(object_id)
        if not object_:
            object_ = await self._get_object_from_elastic(object_id)
            if not object_:
                return None
            await self._put_object_to_cache(object_)
        return object_

    async def _get_object_from_elastic(self, object_id: str):
        doc = await self.elastic.get(self.index, object_id)
        return self.model(**doc['_source'])

    async def _object_from_cache(self, object_id: str):
        data = await self.redis.get(object_id)
        if not data:
            return None
        object_ = self.model.parse_raw(data)
        return object_

    async def _put_object_to_cache(self, object_):
        await self.redis.set(str(object_.id), object_.json(), expire=CACHE_EXPIRE_IN_SECONDS)
