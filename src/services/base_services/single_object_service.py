from typing import Any

from db.redis import AbstractCacheAdapter
from db.elastic import AbstractDBAdapter


class SingleObjectService:
    def __init__(self,
                 db_adapter: AbstractDBAdapter,
                 cache_adapter: AbstractCacheAdapter,
                 index: str,
                 model: Any):
        self.cache_adapter = cache_adapter
        self.db_adapter = db_adapter
        self.model = model
        self.index = index

    async def get_by_id(self, object_id: str):
        obj = await self.cache_adapter.get_objects_from_cache(object_id)
        if obj:
            obj = self.model.parse_raw(obj)
        else:
            obj = await self.db_adapter.get_object_from_db(self.index, self.model, object_id)
            if not obj:
                return None
            json_obj = obj.json()
            await self.cache_adapter.put_objects_to_cache(json_obj, json_obj['id'])
        return obj
