import uuid
from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query
from fastapi.security import HTTPBearer

from core.config import settings
from schemas.review import ReviewListResponse, ReviewRequest, ReviewResponse, ReviewSortKeys
from services.reviews import ReviewsService, get_review_service

router = APIRouter(redirect_slashes=False)


@router.post(
    path="/{movie_id}",
    summary="Добавление рецензии на фильм",
    status_code=HTTPStatus.CREATED,
    dependencies=[Depends(HTTPBearer())],
)
async def add_review(
    request: ReviewRequest,
    movie_id: UUID = Path(..., description="Идентификатор фильма", example=uuid.uuid4()),
    review_service: ReviewsService = Depends(get_review_service),
) -> None:
    await review_service.add_review(movie_id, **request.dict())


@router.delete(
    path="/{movie_id}",
    summary="Удаление рецензии на фильм",
    status_code=HTTPStatus.OK,
    dependencies=[Depends(HTTPBearer())],
)
async def remove_review(
    movie_id: UUID = Path(..., description="Идентификатор фильма", example=uuid.uuid4()),
    review_service: ReviewsService = Depends(get_review_service),
) -> None:
    await review_service.remove_review(movie_id)


@router.get(
    path="/{movie_id}",
    summary="Получение рецензии на фильм",
    status_code=HTTPStatus.OK,
    dependencies=[Depends(HTTPBearer())],
)
async def get_review(
    movie_id: UUID = Path(..., description="Идентификатор фильма", example=uuid.uuid4()),
    review_service: ReviewsService = Depends(get_review_service),
) -> ReviewResponse:
    return await review_service.get_review(movie_id)


@router.post(
    path="/{movie_id}/{review_id}/like",
    summary="Добавление лайка к рецензии на фильм",
    status_code=HTTPStatus.OK,
    dependencies=[Depends(HTTPBearer())],
)
async def like_review(
    movie_id: UUID = Path(..., description="Идентификатор фильма", example=uuid.uuid4()),
    review_id: str = Path(..., description="Идентификатор рецензии", example="65f3876c82f344ecf4de0595"),
    review_service: ReviewsService = Depends(get_review_service),
) -> None:
    await review_service.like(movie_id, review_id)


@router.post(
    path="/{movie_id}/{review_id}/dislike",
    summary="Добавление дизлайка к рецензии на фильм",
    status_code=HTTPStatus.OK,
    dependencies=[Depends(HTTPBearer())],
)
async def dislike_review(
    movie_id: UUID = Path(..., description="Идентификатор фильма", example=uuid.uuid4()),
    review_id: str = Path(..., description="Идентификатор рецензии", example="65f3876c82f344ecf4de0595"),
    review_service: ReviewsService = Depends(get_review_service),
) -> None:
    await review_service.dislike(movie_id, review_id)


@router.delete(
    path="/{movie_id}/{review_id}",
    summary="Удаление оценки к рецензии на фильм",
    status_code=HTTPStatus.OK,
    dependencies=[Depends(HTTPBearer())],
)
async def remove_review_rating(
    movie_id: UUID = Path(..., description="Идентификатор фильма", example=uuid.uuid4()),
    review_id: str = Path(..., description="Идентификатор рецензии", example="65f3876c82f344ecf4de0595"),
    review_service: ReviewsService = Depends(get_review_service),
) -> None:
    await review_service.remove_rating(movie_id, review_id)


@router.get(
    path="/{movie_id}/list",
    summary="Получение список рецензий на фильм",
    status_code=HTTPStatus.OK,
    dependencies=[Depends(HTTPBearer())],
)
async def get_review_list(
    movie_id: UUID = Path(..., description="Идентификатор фильма", example=uuid.uuid4()),
    sort: ReviewSortKeys = Query(default=None, description="Ordering param"),
    page: int = Query(default=1, description="Pagination page number", ge=1),
    page_size: int = Query(
        default=settings.page_size,
        description="Pagination page size",
        ge=1,
        le=settings.page_size_max,
    ),
    review_service: ReviewsService = Depends(get_review_service),
) -> ReviewListResponse:
    return await review_service.get_review_list(movie_id, sort, page, page_size)
