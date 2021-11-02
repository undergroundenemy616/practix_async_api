import uuid
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

    async def get_by_id(self, object_id: uuid.UUID):
        obj = await self.cache_adapter.get_objects_from_cache(str(object_id))
        if obj:
            obj = self.model.parse_raw(obj)
        else:
            obj = await self.db_adapter.get_object_from_db(self.index, self.model, str(object_id))
            if not obj:
                return None
            await self.cache_adapter.put_objects_to_cache(obj.json(), str(object_id))
        return obj
