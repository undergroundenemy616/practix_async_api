import uuid
from typing import List
from datetime import date
import orjson

from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Person(BaseModel):
    id: uuid.UUID
    full_name: str
    roles: List[str] = []
    birth_date: date = None

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps