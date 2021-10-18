import logging
from http import HTTPStatus
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from models.film import FilmListResponseModel, FilmResponseModel
from pydantic import ValidationError

from services.base_services.single_object_service import SingleObjectService
from services.film import FilmsListService, \
    get_list_film_service, FilmSearchService, get_search_list_persons_service, get_retrieve_film_service


router = APIRouter()

logging.basicConfig(level=logging.INFO)


@router.get('', response_model=List[FilmListResponseModel])
async def film_list(sort: str = Query('-rating'),
                    page_size: int = Query(20),
                    page_number: int = Query(1),
                    genre: Optional[str] = None,
                    film_service: FilmsListService = Depends(get_list_film_service)):
    try:
        films_response = await film_service.get_objects(page_size, page_number, genre=genre, sort=sort)
    except ValidationError:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="No such page")
    return [FilmListResponseModel(id=film.id,
                                  title=film.title,
                                  rating=film.rating) for film in films_response]


@router.get('/search', response_model=List[FilmListResponseModel])
async def film_search(query: str = Query(...),
                      page_size: int = Query(20),
                      page_number: int = Query(1),
                      film_service: FilmSearchService = Depends(get_search_list_persons_service)):
    try:
        films_response = await film_service.get_objects(page_size, page_number, query=query)
    except ValidationError:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="No such page")
    return [FilmListResponseModel(id=film.id,
                                  title=film.title,
                                  rating=film.rating) for film in films_response]


@router.get('/{film_id}', response_model=FilmResponseModel)
async def film_details(film_id: str, film_service: SingleObjectService = Depends(get_retrieve_film_service)) -> FilmResponseModel:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
    return FilmResponseModel(id=film.id,
                             title=film.title,
                             rating=film.rating,
                             description=film.description,
                             genre=film.genres,
                             actors=film.actors,
                             writers=film.writers,
                             directors=film.directors)
