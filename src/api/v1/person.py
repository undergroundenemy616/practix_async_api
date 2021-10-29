from http import HTTPStatus

from elasticsearch import NotFoundError
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import ValidationError

from models.person import PersonFilmResponseModel, PersonResponseModel
from services.base_services.single_object_service import SingleObjectService
from services.person import (PersonFilmsListService, PersonSearchListService,
                             get_person_films_service,
                             get_retrieve_person_service,
                             get_search_list_persons_service)

router = APIRouter()


@router.get('/search',
            response_model=list[PersonResponseModel],
            summary="Поиск по персоналиям",
            description="Полнотекстовый поиск по персоналиям",
            response_description="Полное имя, должность и id кинопроизведений, в которых участвовал",
            tags=['Полнотекстовый поиск по персоналиям']
            )
async def person_list(query: str = Query(...),
                      page_size: int = Query(20),
                      page_number: int = Query(1),
                      person_service: PersonSearchListService = Depends(get_search_list_persons_service)):
    try:
        persons_response = await person_service.get_objects(page_size, page_number, query=query)
    except ValidationError:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='No such page')
    except NotFoundError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
    return [PersonResponseModel(id=person.id,
                                full_name=person.full_name,
                                roles=person.roles,
                                film_ids=person.film_ids) for person in persons_response]


@router.get('/{person_id}',
            response_model=PersonResponseModel,
            summary="Страница персоны",
            description="Страница с детализацией по персоне",
            response_description="Полное имя, должность и id кинопроизведений, в которых участвовал",
            tags=['Детализация по персоне']
            )
async def person_details(person_id: str,
                         person_service: SingleObjectService = Depends(get_retrieve_person_service)) -> PersonResponseModel:
    try:
        person = await person_service.get_by_id(person_id)
    except NotFoundError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
    return PersonResponseModel(id=person.id, full_name=person.full_name, roles=person.roles, film_ids=person.film_ids)


@router.get('/{person_id}/films',
            response_model=list[PersonFilmResponseModel],
            summary="Страница кинопроизведений персоны",
            description="Страница с кинопроизведениями, в которых участвовала данная персона",
            response_description="Название и рейтинг кинопроизведения",
            tags=['Кинопроизведения по персоне'],
            deprecated=True)
async def person_films_list(person_id: str,
                            page_size: int = Query(20),
                            page_number: int = Query(1),
                            person_service: PersonFilmsListService = Depends(get_person_films_service)) -> list[PersonFilmResponseModel]:
    try:
        films = await person_service.get_objects(page_size, page_number, person_id=person_id)
    except NotFoundError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='persons films not found')
    return [PersonFilmResponseModel(id=film.id, title=film.title, rating=film.rating) for film in films]
