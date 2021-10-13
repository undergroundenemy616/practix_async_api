import uuid
from typing import List

import orjson

from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class FilmPerson(BaseModel):
    id: uuid.UUID
    name: str


class FilmGenre(BaseModel):
    id: uuid.UUID
    name: str


class Film(BaseModel):
    id: uuid.UUID
    rating: float
    type: str
    title: str
    description: str
    genres_names: List[str] = None
    directors_names: List[str] = None
    actors_names: List[str] = None
    writers_names: List[str] = None
    genres: List[FilmGenre] = []
    directors: List[FilmPerson] = []
    actors: List[FilmPerson] = []
    writers: List[FilmPerson] = []

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps