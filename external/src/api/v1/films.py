from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from api.v1.fields import PageNumberQueryType, PageSizeQueryType
from api.v1.models import FilmDetailExternal, FilmPersonExternal, FilmShortExternal, FilmsSortKeys, GenreExternal
from core.auth import JWTTokenPayload, SystemRolesEnum, check_permissions
from core.config import settings
from core.types import NestedQuery, RequestData
from models.film import Film as FilmInternal
from services.base import BaseService
from services.films import get_films_service

router = APIRouter()


@router.get(
    "/search",
    response_model=list[FilmShortExternal],
    summary="Search films",
    description="Full-text search for film works",
    response_description="Movie title and rating",
    tags=["Full-text search"],
)
async def films_search(
    token: Annotated[JWTTokenPayload | None, Depends(check_permissions())],
    query: Annotated[str, Query(description="Query string for the full text search")],
    sort: Annotated[FilmsSortKeys, Query(description="Ordering param")] = None,
    page_number: PageNumberQueryType = 1,
    page_size: PageSizeQueryType = settings.page_size,
    films_service: BaseService = Depends(get_films_service),
) -> list[FilmShortExternal]:
    """List items with brief information"""

    films: list[FilmInternal] = (
        await films_service.get_data(
            RequestData(
                query=query,
                sort=sort,
                page_number=page_number,
                page_size=page_size,
            ),
        )
        or []
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
    "/{film_id}",
    response_model=FilmDetailExternal,
    summary="Retrieve a film",
    description="Get film work with details",
    response_description="Detailed data on film work with genres and casts",
    tags=["Retrieve details"],
)
async def film_details(
    token: Annotated[JWTTokenPayload | None, Depends(check_permissions(SystemRolesEnum.user))],
    film_id: UUID,
    film_service: BaseService = Depends(get_films_service),
) -> FilmDetailExternal:
    """Retrieve an item with all the information"""

    film: FilmInternal | None = await film_service.get_data(RequestData(id=film_id))
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")

    return FilmDetailExternal(
        uuid=film.id,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genre=[GenreExternal(uuid=genre.id, name=genre.name) for genre in film.genre or []],
        actors=[FilmPersonExternal(uuid=person.id, full_name=person.name) for person in film.actors or []],
        directors=[FilmPersonExternal(uuid=person.id, full_name=person.name) for person in film.directors or []],
        writers=[FilmPersonExternal(uuid=person.id, full_name=person.name) for person in film.writers or []],
    )


@router.get(
    "",
    response_model=list[FilmShortExternal],
    summary="List films",
    description="List film works",
    response_description="Movie title and rating",
    tags=["List"],
)
async def films_list(
    token: Annotated[JWTTokenPayload | None, Depends(check_permissions())],
    sort: Annotated[FilmsSortKeys, Query(description="Ordering param")] = None,
    page_number: PageNumberQueryType = 1,
    page_size: PageSizeQueryType = settings.page_size,
    genre: Annotated[UUID, Query(description="Film work genre")] = None,
    films_service: BaseService = Depends(get_films_service),
) -> list[FilmShortExternal]:
    """List items with brief information"""

    films: list[FilmInternal] = (
        await films_service.get_data(
            RequestData(
                sort=sort,
                page_number=page_number,
                page_size=page_size,
                nested_query=NestedQuery(path="genre", field="id", query_string=str(genre)) if genre else None,
            ),
        )
        or []
    )

    return [
        FilmShortExternal(
            uuid=film.id,
            title=film.title,
            imdb_rating=film.imdb_rating,
        )
        for film in films
    ]
