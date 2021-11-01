from db.redis import AbstractCacheAdapter
from db.elastic import AbstractDBAdapter


class SingleObjectService:
    def __init__(self,
                 db_adapter: AbstractDBAdapter,
                 cache_adapter: AbstractCacheAdapter):
        self.cache_adapter = cache_adapter
        self.db_adapter = db_adapter

    async def get_by_id(self, object_id: str):
        obj = await self.cache_adapter.object_from_cache(object_id)
        if not obj:
            obj = await self.db_adapter.get_object_from_elastic(object_id)
            if not obj:
                return None
            await self.cache_adapter.put_object_to_cache(obj)
        return obj
