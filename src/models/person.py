import uuid
from typing import List
from datetime import date

from pydantic import BaseModel

from utils import CustomBaseModel


class Person(CustomBaseModel):
    id: uuid.UUID
    full_name: str
    roles: List[str] = []
    birth_date: date = None
    film_ids: List[uuid.UUID] = []


class PersonResponseModel(BaseModel):
    id: uuid.UUID
    full_name: str
    roles: List[str] = []
    film_ids: List[uuid.UUID] = []


class PersonListResponseModel(BaseModel):
    total_pages: int
    page: int
    objects: List[PersonResponseModel] = []


class PersonFilmResponseModel(BaseModel):
    id: uuid.UUID
    title: str
    rating: float = None

