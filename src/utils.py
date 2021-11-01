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
    params = f'{index}::{query}::{page_size}::{page_number}'
    hash_object = hashlib.md5(params.encode())
    return hash_object.hexdigest()
