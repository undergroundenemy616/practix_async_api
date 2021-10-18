import logging
from http import HTTPStatus
from typing import List

from elasticsearch import NotFoundError
from fastapi import APIRouter, Depends, HTTPException, Query

from models.genre import GenreResponseModel
from services.base_services.single_object_service import SingleObjectService
from services.genre import (GenresListService, get_genre_list_service,
                            get_genre_retrieve_service)

router = APIRouter()

logging.basicConfig(level=logging.INFO)


@router.get('/{genre_id}', response_model=GenreResponseModel)
async def genre_details(genre_id: str, genre_service: SingleObjectService = Depends(get_genre_retrieve_service)) -> GenreResponseModel:
    try:
        genre = await genre_service.get_by_id(genre_id)
    except NotFoundError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')

    return GenreResponseModel(id=genre.id, name=genre.name, description=genre.description)


@router.get('', response_model=List[GenreResponseModel], response_model_exclude={'description'})
async def genres_list(
        amount: int = Query(100),
        page_size: int = Query(20),
        page_number: int = Query(1),
        genre_service: GenresListService = Depends(get_genre_list_service)) -> List[GenreResponseModel]:
    try:
        genres = await genre_service.get_objects(page_size, page_number, size=amount)
    except NotFoundError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genres not found')
    return [GenreResponseModel(id=genre.id, name=genre.name) for genre in genres]
