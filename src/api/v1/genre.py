import uuid
from http import HTTPStatus
from typing import List

from elasticsearch import NotFoundError
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from services.genre.genre_detailed import GenreService, get_genre_service
from services.genre.genre_list import GenresListService, get_genre_list_service

router = APIRouter()


class Genre(BaseModel):
    id: uuid.UUID
    name: str
    description: str = None


@router.get('/{genre_id}', response_model=Genre)
async def genre_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    try:
        genre = await genre_service.get_by_id(genre_id)
    except NotFoundError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')

    return Genre(id=genre.id, name=genre.name, description=genre.description)


@router.get('', response_model=List[Genre], response_model_exclude={'description'})
async def genres_list(
        amount: int = Query(100),
        genre_service: GenresListService = Depends(get_genre_list_service)) -> List[Genre]:
    genres = await genre_service.get_genres(amount)
    return [Genre(id=genre.id, name=genre.name) for genre in genres]
