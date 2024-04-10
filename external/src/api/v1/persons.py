import itertools
from http import HTTPStatus
from itertools import groupby
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from api.v1.fields import PageNumberQueryType, PageSizeQueryType
from api.v1.models import FilmShortExternal, FilmsSortKeys, PersonDetailExternal, PersonFilmExternal
from core.auth import JWTTokenPayload, SystemRolesEnum, check_permissions
from core.config import settings
from core.types import NestedQuery, RequestData
from models.person import Person as PersonInternal
from services.base import BaseService
from services.films import get_films_service
from services.persons import get_persons_service

router = APIRouter()


@router.get(
    "/search",
    response_model=list[PersonDetailExternal],
    summary="Search persons",
    description="Full-text search for persons",
    response_description="Person name with films and roles",
    tags=["Full-text search"],
)
async def persons_list(
    token: Annotated[JWTTokenPayload | None, Depends(check_permissions())],
    query: Annotated[str, Query(description="Query string for the full text search")],
    page_number: PageNumberQueryType = 1,
    page_size: PageSizeQueryType = settings.page_size,
    persons_service: BaseService = Depends(get_persons_service),
) -> list[PersonDetailExternal]:
    """List items with brief information"""

    persons: list[PersonInternal] = (
        await persons_service.get_data(
            RequestData(
                query=query,
                page_number=page_number,
                page_size=page_size,
            ),
        )
        or []
    )

    return [
        PersonDetailExternal(
            uuid=person.id,
            full_name=person.name,
            films=[
                PersonFilmExternal(uuid=film_id, roles=[film.role for film in group])
                for film_id, group in groupby(person.films, key=lambda x: x.id) or []  # type: ignore
            ],
        )
        for person in persons
    ]


@router.get(
    "/{person_id}/film",
    response_model=list[FilmShortExternal],
    summary="List person films",
    description="List film works of a person",
    response_description="Movie title and rating",
    tags=["List"],
)
async def person_films_list(
    token: Annotated[JWTTokenPayload | None, Depends(check_permissions())],
    person_id: UUID,
    sort: Annotated[FilmsSortKeys, Query(description="Ordering param")] = None,
    page_number: PageNumberQueryType = 1,
    page_size: PageSizeQueryType = settings.page_size,
    films_service: BaseService = Depends(get_films_service),
) -> list[FilmShortExternal]:
    """List person films with brief information"""
    films = itertools.chain.from_iterable(
        [
            await films_service.get_data(
                RequestData(
                    sort=sort,
                    page_number=page_number,
                    page_size=page_size,
                    nested_query=NestedQuery(path=path, field="id", query_string=str(person_id)),
                ),
            )
            or []
            for path in ("actors", "writers", "directors")
        ],
    )

    return [
        FilmShortExternal(
            uuid=film.id,
            title=film.title,
            imdb_rating=film.imdb_rating,
        )
        for film in films
    ]


@router.get(
    "/{person_id}",
    response_model=PersonDetailExternal,
    summary="Retrieve a person",
    description="Get person with details",
    response_description="Persons name with films and roles",
    tags=["Retrieve details"],
)
async def person_details(
    token: Annotated[JWTTokenPayload | None, Depends(check_permissions(SystemRolesEnum.user))],
    person_id: UUID,
    person_service: BaseService = Depends(get_persons_service),
) -> PersonDetailExternal:
    """Retrieve an item with all the information"""

    person: PersonInternal | None = await person_service.get_data(RequestData(id=person_id))
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")

    return PersonDetailExternal(
        uuid=person.id,
        full_name=person.name,
        films=[
            PersonFilmExternal(uuid=film_id, roles=[film.role for film in group])
            for film_id, group in groupby(person.films, key=lambda x: x.id) or []  # type: ignore
        ],
    )
