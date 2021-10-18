import orjson
from pydantic import BaseModel

CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут

def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class CustomBaseModel(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
