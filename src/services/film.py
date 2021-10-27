from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic, ElasticAdapter
from db.redis import get_redis, RedisAdapter
from models.film import Film
from services.base_services.list_object_service import BaseListService
from services.base_services.single_object_service import SingleObjectService


class FilmsListService(BaseListService):

    @staticmethod
    def get_elastic_query(genre: Optional[str], sort: Optional[str]) -> dict:
        field = sort.lstrip('-')
        query = {
            'sort':
                {
                    field: {'order': 'desc' if sort.startswith('-') else 'asc'}
                }
        }
        if genre:
            query['query'] = {'bool': {
                'must':
                    {
                        'nested': {
                            'path': 'genres',
                            'query': {
                                'bool': {
                                    'should':
                                        {'term': {'genres.id': genre}}
                                }
                            }
                        }
                    }
            }
            }
        return query


class FilmSearchService(BaseListService):

    @staticmethod
    def get_elastic_query(query: str) -> dict:
        query = {'query': {
            'multi_match': {
                'query': query,
                'fields': ['title', 'description']
            }
        }
    }
        return query


@lru_cache()
def get_list_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmsListService:
    index = 'filmwork'
    model = Film
    cache_adapter = RedisAdapter(redis_instance=redis, model=model, index=index)
    db_adapter = ElasticAdapter(elastic=elastic, model=model, index=index)
    return FilmsListService(cache_adapter=cache_adapter, db_adapter=db_adapter)


@lru_cache()
def get_search_list_persons_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmSearchService:
    index = 'filmwork'
    model = Film
    cache_adapter = RedisAdapter(redis_instance=redis, model=model, index=index)
    db_adapter = ElasticAdapter(elastic=elastic, model=model, index=index)
    return FilmSearchService(cache_adapter=cache_adapter, db_adapter=db_adapter)


@lru_cache()
def get_retrieve_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> SingleObjectService:
    index = 'filmwork'
    model = Film
    cache_adapter = RedisAdapter(redis_instance=redis, model=model, index=index)
    db_adapter = ElasticAdapter(elastic=elastic, model=model, index=index)
    return SingleObjectService(cache_adapter=cache_adapter, db_adapter=db_adapter)
