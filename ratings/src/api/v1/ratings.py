import uuid
from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, Path
from fastapi.security import HTTPBearer

from schemas.ratings import RatingsResponse
from services.ratings import RatingsService, get_ratings_service

router = APIRouter(redirect_slashes=False)


@router.post(
    path="/{movie_id}/like",
    summary="Добавление лайка фильму",
    status_code=HTTPStatus.OK,
    dependencies=[Depends(HTTPBearer())],
)
async def like_movie(
    movie_id: UUID = Path(..., description="Идентификатор фильма", example=uuid.uuid4()),
    ratings_service: RatingsService = Depends(get_ratings_service),
) -> None:
    await ratings_service.like(movie_id)


@router.post(
    path="/{movie_id}/dislike",
    summary="Добавление дизлайка фильму",
    status_code=HTTPStatus.OK,
    dependencies=[Depends(HTTPBearer())],
)
async def dislike_movie(
    movie_id: UUID = Path(..., description="Идентификатор фильма", example=uuid.uuid4()),
    ratings_service: RatingsService = Depends(get_ratings_service),
) -> None:
    await ratings_service.dislike(movie_id)


@router.post(
    path="/{movie_id}/{rating}",
    summary="Добавление рейтинга фильму",
    status_code=HTTPStatus.OK,
    dependencies=[Depends(HTTPBearer())],
)
async def set_rating(
    movie_id: UUID = Path(..., description="Идентификатор фильма", example=uuid.uuid4()),
    rating: int = Path(default=..., description="Значение рейтинга", example=5, gt=0, lt=10),
    ratings_service: RatingsService = Depends(get_ratings_service),
) -> None:
    await ratings_service.set_rating(movie_id, rating)


@router.delete(
    path="/{movie_id}/",
    summary="Удаление рейтинга фильму",
    status_code=HTTPStatus.OK,
    dependencies=[Depends(HTTPBearer())],
)
async def remove_rating(
    movie_id: UUID = Path(..., description="Идентификатор фильма", example=uuid.uuid4()),
    ratings_service: RatingsService = Depends(get_ratings_service),
) -> None:
    await ratings_service.remove_rating(movie_id)


@router.get(
    path="/{movie_id}",
    summary="Получение рейтинга фильма",
    status_code=HTTPStatus.OK,
    dependencies=[Depends(HTTPBearer())],
)
async def get_ratings(
    movie_id: UUID = Path(..., description="Идентификатор фильма", example=uuid.uuid4()),
    ratings_service: RatingsService = Depends(get_ratings_service),
) -> RatingsResponse:
    return await ratings_service.get_rating(movie_id)
