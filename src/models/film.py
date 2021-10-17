import uuid
from typing import List

from pydantic import BaseModel

from utils import CustomBaseModel


class FilmPerson(BaseModel):
    id: uuid.UUID
    name: str


class FilmGenre(BaseModel):
    id: uuid.UUID
    name: str


class Film(CustomBaseModel):
    id: str
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


class FilmResponseModel(BaseModel):
    id: str
    title: str
    rating: float
    description: str
    genre: List[FilmGenre]
    actors: List[FilmPerson]
    writers: List[FilmPerson]
    directors: List[FilmPerson]


class FilmListResponseModel(BaseModel):
    id: uuid.UUID
    title: str
    rating: float
