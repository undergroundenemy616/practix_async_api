from db.redis import AbstractCacheAdapter
from db.elastic import AbstractDBAdapter


class SingleObjectService:
    def __init__(self,
                 db_adapter: AbstractDBAdapter,
                 cache_adapter: AbstractCacheAdapter):
        self.cache_adapter = cache_adapter
        self.db_adapter = db_adapter

    async def get_by_id(self, object_id: str):
        object_ = await self.cache_adapter.object_from_cache(object_id)
        if not object_:
            object_ = await self.db_adapter.get_object_from_elastic(object_id)
            if not object_:
                return None
            await self.cache_adapter.put_object_to_cache(object_)
        return object_
