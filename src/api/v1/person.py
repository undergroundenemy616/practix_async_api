import uuid
from http import HTTPStatus
from typing import List

from elasticsearch import NotFoundError
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ValidationError

from services.person.person_detailed import PersonService, get_person_service
from services.person.person_search_list import PersonSearchListService, get_search_list_persons_service
from services.person.person_films_list import PersonFilmsListService, get_person_films_service

router = APIRouter()


class Person(BaseModel):
    id: uuid.UUID
    full_name: str
    roles: List[str] = []
    film_ids: List[uuid.UUID] = []


class PersonListResponse(BaseModel):
    total_pages: int
    page: int
    objects: List[Person] = []


class PersonFilm(BaseModel):
    id: uuid.UUID
    title: str
    rating: float = None


@router.get('/search', response_model=PersonListResponse)
async def person_list(query: str = Query(...),
                      page_size: int = Query(20),
                      page_number: int = Query(1),
                      person_service: PersonSearchListService = Depends(get_search_list_persons_service)):
    try:
        persons_response = await person_service.get_search_persons(query, page_size, page_number)
    except ValidationError:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="No such page")
    return PersonListResponse(total_pages=persons_response.total_pages,
                              page=persons_response.page,
                              objects=persons_response.objects)


@router.get('/{person_id}', response_model=Person)
async def person_details(person_id: str,
                         person_service: PersonService = Depends(get_person_service)) -> Person:
    try:
        person = await person_service.get_by_id(person_id)
    except NotFoundError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
    return Person(id=person.id, full_name=person.full_name, roles=person.roles, film_ids=person.film_ids)


@router.get('/{person_id}/films', response_model=List[PersonFilm], deprecated=True)
async def person_details(person_id: str,
                         person_service: PersonFilmsListService = Depends(get_person_films_service)) -> List[PersonFilm]:
    try:
        films = await person_service.get_person_films(person_id)
    except NotFoundError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
    return [PersonFilm(id=film.id, title=film.title, rating=film.rating) for film in films]


