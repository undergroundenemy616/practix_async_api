from abc import abstractmethod
from typing import Any, Optional

import backoff as backoff
from elasticsearch import AsyncElasticsearch, ConnectionError

es: Optional[AsyncElasticsearch] = None


class AbstractDBAdapter:

    @abstractmethod
    async def get_objects_from_db(self, *args):
        pass

    @abstractmethod
    async def get_object_from_db(self, *args):
        pass


class ElasticAdapter(AbstractDBAdapter):
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    @backoff.on_exception(backoff.expo, ConnectionError)
    async def get_objects_from_db(self, index: str, model: Any, query: dict, page_size: int, page_number: int) -> list:
        from_ = page_size * (page_number - 1)
        data = await self.elastic.search(index=index,
                                         body=query,
                                         size=page_size,
                                         from_=from_)

        hits = data['hits']['hits']
        return [model(**document['_source']) for document in hits]

    @backoff.on_exception(backoff.expo, ConnectionError)
    async def get_object_from_db(self, index: str, model: Any, object_id: str):
        doc = await self.elastic.get(index, object_id)
        return model(**doc['_source'])


async def get_elastic() -> ElasticAdapter:
    return ElasticAdapter(elastic=es)
