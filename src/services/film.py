from functools import lru_cache
from typing import Optional

from fastapi import Depends

from db.elastic import ElasticAdapter, get_elastic
from db.redis import RedisAdapter, get_redis
from models.film import Film
from services.base_services.list_object_service import BaseListService
from services.base_services.single_object_service import SingleObjectService


class FilmsListService(BaseListService):

    @staticmethod
    def get_elastic_query(genre: Optional[str], sort: Optional[str], degrading: bool = False) -> dict:
        field = sort.lstrip('-')
        query = {
            'sort':
                {
                    field: {'order': 'desc' if sort.startswith('-') else 'asc'}
                },
            'query':
                {'bool': {}}
        }
        if genre:
            query['query']['bool']['must'] = {
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

        if degrading:
            query['query']['bool']['filter'] = {
                        "range": {
                            "rating": {"lt": 7}
                        },
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
        redis: RedisAdapter = Depends(get_redis),
        elastic: ElasticAdapter = Depends(get_elastic),
) -> FilmsListService:
    return FilmsListService(cache_adapter=redis, db_adapter=elastic, index='filmwork', model=Film)


@lru_cache()
def get_search_list_persons_service(
        redis: RedisAdapter = Depends(get_redis),
        elastic: ElasticAdapter = Depends(get_elastic),
) -> FilmSearchService:
    return FilmSearchService(cache_adapter=redis, db_adapter=elastic, index='filmwork', model=Film)


@lru_cache()
def get_retrieve_film_service(
        redis: RedisAdapter = Depends(get_redis),
        elastic: ElasticAdapter = Depends(get_elastic),
) -> SingleObjectService:
    return SingleObjectService(cache_adapter=redis, db_adapter=elastic, index='filmwork', model=Film)
