import uuid
from typing import List

import orjson

from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class FilmPerson(BaseModel):
    id: uuid.UUID
    full_name: str


class FilmGenre(BaseModel):
    id: uuid.UUID
    name: str


class Film(BaseModel):
    id: uuid.UUID
    rating: float
    type: str
    title: str
    description: str
    genres_names: List[str] = []
    directors_names: List[str] = []
    actors_names: List[str] = []
    writers_names: List[str] = []
    genres: List[FilmGenre] = []
    directors: List[FilmPerson] = []
    actors: List[FilmPerson] = []
    writers: List[FilmPerson] = []

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps