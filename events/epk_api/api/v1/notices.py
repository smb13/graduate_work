from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, Header
from fastapi.security import HTTPBearer

from schemas.error import HttpExceptionModel
from schemas.requests import GeneralNoticeRequest, ReviewLikeRequest, WeeklyBookmarksRequest
from schemas.responses import NoticeCreationResponse
from services.notice import NoticeService, get_notice_service

router = APIRouter(redirect_slashes=False, prefix="", tags=["EPK API"])


@router.post(
    "/review_like",
    summary="Отправка нотификацию о лайке или дизлаке рецензии",
    response_model=NoticeCreationResponse,
    status_code=HTTPStatus.CREATED,
    responses={
        HTTPStatus.BAD_REQUEST: {"model": HttpExceptionModel},
        HTTPStatus.UNAUTHORIZED: {"model": HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {"model": HttpExceptionModel},
        HTTPStatus.UNPROCESSABLE_ENTITY: {"model": HttpExceptionModel},
        HTTPStatus.INTERNAL_SERVER_ERROR: {"model": HttpExceptionModel},
    },
    dependencies=[Depends(HTTPBearer())],
)
async def create_review_like(
    review_like: ReviewLikeRequest,
    notice_service: NoticeService = Depends(get_notice_service),
    x_request_id: Annotated[str | None, Header()] = None,
) -> NoticeCreationResponse:
    return await notice_service.create_review_like(
        request=review_like,
        x_request_id=x_request_id,
    )


@router.post(
    "/weekly_bookmarks",
    summary="Отправка всем пользователям закладки сделанные за неделю",
    response_model=NoticeCreationResponse,
    status_code=HTTPStatus.CREATED,
    responses={
        HTTPStatus.BAD_REQUEST: {"model": HttpExceptionModel},
        HTTPStatus.UNAUTHORIZED: {"model": HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {"model": HttpExceptionModel},
        HTTPStatus.UNPROCESSABLE_ENTITY: {"model": HttpExceptionModel},
        HTTPStatus.INTERNAL_SERVER_ERROR: {"model": HttpExceptionModel},
    },
    dependencies=[Depends(HTTPBearer())],
)
async def create_weekly_bookmarks(
    weekly_bookmarks: WeeklyBookmarksRequest,
    notice_service: NoticeService = Depends(get_notice_service),
    x_request_id: Annotated[str | None, Header()] = None,
) -> NoticeCreationResponse:
    return await notice_service.create_weekly_bookmarks(
        request=weekly_bookmarks,
        x_request_id=x_request_id,
    )


@router.post(
    "/general_notice",
    summary="Отправка Отправить пользователю(ям) сообщение",
    response_model=NoticeCreationResponse,
    status_code=HTTPStatus.CREATED,
    responses={
        HTTPStatus.BAD_REQUEST: {"model": HttpExceptionModel},
        HTTPStatus.UNAUTHORIZED: {"model": HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {"model": HttpExceptionModel},
        HTTPStatus.UNPROCESSABLE_ENTITY: {"model": HttpExceptionModel},
        HTTPStatus.INTERNAL_SERVER_ERROR: {"model": HttpExceptionModel},
    },
    dependencies=[Depends(HTTPBearer())],
)
async def create_general_notice(
    general_notice: GeneralNoticeRequest,
    notice_service: NoticeService = Depends(get_notice_service),
    x_request_id: Annotated[str | None, Header()] = None,
) -> NoticeCreationResponse:
    return await notice_service.create_create_general_notice(
        request=general_notice,
        x_request_id=x_request_id,
    )
