import logging
import uuid
from http import HTTPStatus
from typing import Optional

from elasticsearch import NotFoundError
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import ValidationError

from auth_grpc.auth_check import check_permission
from models.film import FilmListResponseModel, FilmResponseModel
from services.base_services.single_object_service import SingleObjectService
from services.film import (FilmSearchService, FilmsListService,
                           get_list_film_service, get_retrieve_film_service,
                           get_search_list_persons_service)

router = APIRouter()

logging.basicConfig(level=logging.INFO)


@router.get('',
            response_model=list[FilmListResponseModel],
            summary="Список кинопроизведений",
            description="Список кинопроизведений, отсортированный по рейтингу. "
                        "По умолчанию - 20 объектов на страницу",
            response_description="Название и рейтинг фильма",
            tags=['Список кинопроизведений']
            )
@check_permission(roles=["Subscriber"])
async def film_list(
        request: Request,
        sort: str = Query('-rating'),
        page_size: int = Query(20),
        page_number: int = Query(1),
        genre: Optional[str] = None,
        degrading: bool = False,
        film_service: FilmsListService = Depends(get_list_film_service)):
    try:
        films_response = await film_service.get_objects(page_size, page_number, genre=genre,
                                                        sort=sort, degrading=degrading)
    except ValidationError:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="No such page")
    except NotFoundError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')
    return [FilmListResponseModel(id=film.id,
                                  title=film.title,
                                  rating=film.rating) for film in films_response]


@router.get('/search',
            response_model=list[FilmListResponseModel],
            summary="Поиск кинопроизведений",
            description="Полнотекстовый поиск по кинопроизведениям",
            response_description="Название и рейтинг кинопроизведения",
            tags=['Полнотекстовый поиск по кинопроизведениям']
            )
async def film_search(query: str = Query(...),
                      page_size: int = Query(20),
                      page_number: int = Query(1),
                      film_service: FilmSearchService = Depends(get_search_list_persons_service)):
    try:
        films_response = await film_service.get_objects(page_size, page_number, query=query)
    except ValidationError:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="No such page")
    except NotFoundError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')
    return [FilmListResponseModel(**film.dict()) for film in films_response]


@router.get('/{film_id}',
            response_model=FilmResponseModel,
            summary="Страница кинопроизведения",
            description="Страница с детализацией по кинопроизведению",
            response_description="Название, рейтинг, описание, жанры, актеры, сценаристы и режиссеры кинопроизведения",
            tags=['Детализация кинопроизведения']
            )
async def film_details(film_id: uuid.UUID,
                       film_service: SingleObjectService = Depends(get_retrieve_film_service)) -> FilmResponseModel:
    try:
        film = await film_service.get_by_id(film_id)
    except NotFoundError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
    return FilmResponseModel(**film.dict())
