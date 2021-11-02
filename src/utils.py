import hashlib

import orjson
from pydantic import BaseModel

CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class CustomBaseModel(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


def get_redis_key_hash(index, query, page_size, page_number):
    params = f'{query}{page_size}{page_number}'
    hash_string = hashlib.md5(params.encode()).hexdigest()
    return f'elastic_cache::{index}::{hash_string}'


