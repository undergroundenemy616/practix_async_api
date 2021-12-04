import json
from abc import abstractmethod
from typing import Any

from db.elastic import AbstractDBAdapter
from db.redis import AbstractCacheAdapter
from utils import get_redis_key_hash


class BaseListService:
    def __init__(self,
                 db_adapter: AbstractDBAdapter,
                 cache_adapter: AbstractCacheAdapter,
                 index: str,
                 model: Any):
        self.cache_adapter = cache_adapter
        self.db_adapter = db_adapter
        self.model = model
        self.index = index

    @staticmethod
    @abstractmethod
    def get_elastic_query(**kwargs):
        pass

    async def get_objects(self,
                          page_size: int = 100,
                          page_number: int = 0,
                          **kwargs) -> list:
        query = self.get_elastic_query(**kwargs)
        redis_key = get_redis_key_hash(self.index, query, page_size, page_number)
        objects = await self.cache_adapter.get_objects_from_cache(redis_key)
        if objects:
            objects = [self.model.parse_raw(document) for document in json.loads(objects)]
        else:
            objects = await self.db_adapter.get_objects_from_db(self.index, self.model, query, page_size, page_number)
            if not objects:
                return []
            json_objects = json.dumps([document.json() for document in objects])
            await self.cache_adapter.put_objects_to_cache(json_objects, redis_key)
        return objects

