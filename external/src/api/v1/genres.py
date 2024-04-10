from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from api.v1.fields import PageNumberQueryType, PageSizeQueryType
from api.v1.models import GenreExternal
from core.auth import JWTTokenPayload, SystemRolesEnum, check_permissions
from core.config import settings
from core.types import RequestData
from models.genre import Genre as GenreInternal
from services.base import BaseService
from services.genres import get_genres_service

router = APIRouter()


@router.get(
    "/{genre_id}",
    response_model=GenreExternal,
    summary="Retrieve a genre",
    description="Get genre with details",
    response_description="Detailed data on genres",
    tags=["Retrieve details"],
)
async def genre_details(
    token: Annotated[JWTTokenPayload | None, Depends(check_permissions(SystemRolesEnum.user))],
    genre_id: UUID,
    genre_service: BaseService = Depends(get_genres_service),
) -> GenreExternal:
    """Retrieve an item with all the information"""

    genre: GenreInternal | None = await genre_service.get_data(RequestData(id=genre_id))
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")

    return GenreExternal(
        uuid=genre.id,
        name=genre.name,
    )


@router.get(
    "",
    response_model=list[GenreExternal],
    summary="List genres",
    description="List of genres",
    response_description="Genre name",
    tags=["List"],
)
async def genres_list(
    token: Annotated[JWTTokenPayload | None, Depends(check_permissions())],
    page_number: PageNumberQueryType = 1,
    page_size: PageSizeQueryType = settings.page_size,
    genres_service: BaseService = Depends(get_genres_service),
) -> list[GenreExternal]:
    """List items with brief information"""

    genres: list[GenreInternal] = (
        await genres_service.get_data(
            RequestData(
                page_number=page_number,
                page_size=page_size,
            ),
        )
        or []
    )
    return [GenreExternal(uuid=genre.id, name=genre.name) for genre in genres]
