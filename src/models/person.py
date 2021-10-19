import uuid
from datetime import date

from pydantic import BaseModel

from utils import CustomBaseModel


class Person(CustomBaseModel):
    id: uuid.UUID
    full_name: str
    roles: list[str] = []
    birth_date: date = None
    film_ids: list[uuid.UUID] = []


class PersonResponseModel(BaseModel):
    id: uuid.UUID
    full_name: str
    roles: list[str] = []
    film_ids: list[uuid.UUID] = []


class PersonFilmResponseModel(BaseModel):
    id: uuid.UUID
    title: str
    rating: float = None

