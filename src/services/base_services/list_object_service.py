from abc import abstractmethod
from db.redis import AbstractCacheAdapter
from db.elastic import AbstractDBAdapter


class BaseListService:
    def __init__(self,
                 db_adapter: AbstractDBAdapter,
                 cache_adapter: AbstractCacheAdapter):
        self.cache_adapter = cache_adapter
        self.db_adapter = db_adapter

    @staticmethod
    @abstractmethod
    def get_elastic_query(**kwargs):
        pass

    async def get_objects(self,
                          page_size: int = 100,
                          page_number: int = 0,
                          **kwargs) -> list:
        query = self.get_elastic_query(**kwargs)
        objects = await self.cache_adapter.get_objects_from_cache(query, page_size, page_number)
        if not objects:
            objects = await self.db_adapter.get_objects_from_elastic(query, page_size, page_number)
            if not objects:
                return []
            await self.cache_adapter.put_objects_to_cache(objects, query, page_size, page_number)
        return objects

