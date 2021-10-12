import uuid
import orjson

from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Genre(BaseModel):
    id: uuid.UUID
    name: str
    description: str = None

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps