import logging
import uuid
from http import HTTPStatus

from elasticsearch import NotFoundError
from fastapi import APIRouter, Depends, HTTPException, Query, Request

from models.genre import GenreResponseModel
from services.base_services.single_object_service import SingleObjectService
from services.genre import (GenresListService, get_genre_list_service,
                            get_genre_retrieve_service)

router = APIRouter()

logging.basicConfig(level=logging.INFO)


@router.get('/{genre_id}',
            response_model=GenreResponseModel,
            summary="Страница жанра",
            description="Страница с детализацией по жанру",
            response_description="Название, описание жанра",
            tags=['Детализация жанра']
            )
async def genre_details(genre_id: uuid.UUID,
                        genre_service: SingleObjectService = Depends(get_genre_retrieve_service)) -> GenreResponseModel:
    try:
        genre = await genre_service.get_by_id(genre_id)
    except NotFoundError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')

    return GenreResponseModel(**genre.dict())


@router.get('',
            response_model=list[GenreResponseModel],
            summary="Список жанров",
            description="Список жанров, По умолчанию - 20 объектов на страницу",
            response_description="Название жанров",
            tags=['Список жанров'],
            response_model_exclude={'description'})
async def genres_list(
        request: Request,
        amount: int = Query(100),
        page_size: int = Query(20),
        page_number: int = Query(1),
        genre_service: GenresListService = Depends(get_genre_list_service)) -> list[GenreResponseModel]:
    try:
        genres = await genre_service.get_objects(page_size, page_number, size=amount)
    except NotFoundError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genres not found')
    return [GenreResponseModel(**genre.dict()) for genre in genres]
