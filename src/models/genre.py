import uuid

from pydantic import BaseModel

from utils import CustomBaseModel


class Genre(CustomBaseModel):
    id: uuid.UUID
    name: str
    description: str = None


class GenreResponseModel(BaseModel):
    id: uuid.UUID
    name: str
    description: str = None
