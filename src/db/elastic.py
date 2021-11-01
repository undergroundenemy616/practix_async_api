from typing import Optional, Any

import backoff as backoff
from elasticsearch import AsyncElasticsearch, ConnectionError
from abc import abstractmethod

es: Optional[AsyncElasticsearch] = None


async def get_elastic() -> AsyncElasticsearch:
    return es


class AbstractDBAdapter:

    @abstractmethod
    async def get_objects_from_elastic(self, *args):
        pass

    @abstractmethod
    async def get_object_from_elastic(self, *args):
        pass


class ElasticAdapter(AbstractDBAdapter):
    def __init__(self, elastic: AsyncElasticsearch, model: Any, index: str):
        self.elastic = elastic
        self.model = model
        self.index = index

    @backoff.on_exception(backoff.expo, ConnectionError)
    async def get_objects_from_elastic(self, query: dict, page_size: int, page_number: int) -> list:
        from_ = page_size * (page_number - 1)
        data = await self.elastic.search(index=self.index,
                                         body=query,
                                         size=page_size,
                                         from_=from_)

        hits = data['hits']['hits']
        return [self.model(**document['_source']) for document in hits]

    @backoff.on_exception(backoff.expo, ConnectionError)
    async def get_object_from_elastic(self, object_id: str):
        doc = await self.elastic.get(self.index, object_id)
        return self.model(**doc['_source'])
