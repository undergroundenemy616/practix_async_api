import uuid

from pydantic import BaseModel

from utils import CustomBaseModel


class FilmPerson(BaseModel):
    id: uuid.UUID
    name: str


class FilmGenre(BaseModel):
    id: uuid.UUID
    name: str


class Film(CustomBaseModel):
    id: uuid.UUID
    rating: float
    type: str
    title: str
    description: str = None
    genres_names: list[str] = None
    directors_names: list[str] = None
    actors_names: list[str] = None
    writers_names: list[str] = None
    genres: list[FilmGenre] = []
    directors: list[FilmPerson] = []
    actors: list[FilmPerson] = []
    writers: list[FilmPerson] = []


class FilmResponseModel(BaseModel):
    id: uuid.UUID
    title: str
    rating: float
    description: str = None
    genres: list[FilmGenre] = []
    actors: list[FilmPerson] = []
    writers: list[FilmPerson] = []
    directors: list[FilmPerson] = []


class FilmListResponseModel(BaseModel):
    id: uuid.UUID
    title: str
    rating: float
