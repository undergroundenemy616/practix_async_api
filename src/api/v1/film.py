import logging
import uuid
from http import HTTPStatus
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from models.film import FilmGenre, FilmPerson
from pydantic import BaseModel, ValidationError
from services.film.film import FilmService, get_film_service
from services.film.film_list import FilmsListService, get_list_film_service
from services.film.film_search_list import (FilmSearchService,
                                            get_search_list_persons_service)

router = APIRouter()

logging.basicConfig(level=logging.INFO)


class Film(BaseModel):
    id: str
    title: str
    rating: float
    description: str
    genre: List[FilmGenre]
    actors: List[FilmPerson]
    writers: List[FilmPerson]
    directors: List[FilmPerson]


class FilmList(BaseModel):
    id: uuid.UUID
    title: str
    rating: float


@router.get('', response_model=List[FilmList])
async def film_list(sort: str = Query('-rating'),
                    page_size: int = Query(20),
                    page_number: int = Query(1),
                    genre: Optional[str] = None,
                    film_service: FilmsListService = Depends(get_list_film_service)):
    try:
        films_response = await film_service.get_films(page_size, page_number, genre=genre, sort=sort)
    except ValidationError:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="No such page")
    return [FilmList(id=film.id,
                     title=film.title,
                     rating=film.rating) for film in films_response]


@router.get('/search', response_model=List[FilmList])
async def film_search(query: str = Query(...),
                      page_size: int = Query(20),
                      page_number: int = Query(1),
                      film_service: FilmSearchService = Depends(get_search_list_persons_service)):
    try:
        films_response = await film_service.get_films(page_size, page_number, query=query)
    except ValidationError:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="No such page")
    return [FilmList(id=film.id,
                     title=film.title,
                     rating=film.rating) for film in films_response]


@router.get('/{film_id}', response_model=Film)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
    return Film(id=film.id,
                title=film.title,
                rating=film.rating,
                description=film.description,
                genre=film.genres,
                actors=film.actors,
                writers=film.writers,
                directors=film.directors)
