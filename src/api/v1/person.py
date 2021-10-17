from http import HTTPStatus
from typing import List

from elasticsearch import NotFoundError
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import ValidationError

from models.person import PersonListResponseModel, PersonResponseModel, PersonFilmResponseModel

from services.single_object_service import SingleObjectService, get_person_service
from services.person.person_search_list import PersonSearchListService, get_search_list_persons_service
from services.person.person_films_list import PersonFilmsListService, get_person_films_service

router = APIRouter()


@router.get('/search', response_model=PersonListResponseModel)
async def person_list(query: str = Query(...),
                      page_size: int = Query(20),
                      page_number: int = Query(1),
                      person_service: PersonSearchListService = Depends(get_search_list_persons_service)):
    try:
        persons_response = await person_service.get_search_persons(query, page_size, page_number)
    except ValidationError:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="No such page")
    except NotFoundError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
    return PersonListResponseModel(total_pages=persons_response.total_pages,
                                   page=persons_response.page,
                                   objects=persons_response.objects)


@router.get('/{person_id}', response_model=PersonResponseModel)
async def person_details(person_id: str,
                         person_service: SingleObjectService = Depends(get_person_service)) -> PersonResponseModel:
    try:
        person = await person_service.get_by_id(person_id)
    except NotFoundError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
    return PersonResponseModel(id=person.id, full_name=person.full_name, roles=person.roles, film_ids=person.film_ids)


@router.get('/{person_id}/films', response_model=List[PersonFilmResponseModel], deprecated=True)
async def person_films_list(person_id: str,
                            person_service: PersonFilmsListService = Depends(get_person_films_service)) -> List[
    PersonFilmResponseModel]:
    # try:
    films = await person_service.get_person_films(person_id)
    # except NotFoundError:
    #     raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films of a person are not found')
    return [PersonFilmResponseModel(id=film.id, title=film.title, rating=film.rating) for film in films]
