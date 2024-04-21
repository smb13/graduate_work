from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends

from schemas.error import HttpExceptionModel
from services.access import security_jwt, check_access, Roles
from services.me_user_subscription import MeUserSubscriptionService, get_me_user_subscription_service

router = APIRouter(redirect_slashes=False, prefix="/user_subscriptions", tags=['User subscriptions internal'])


@router.post(
    '/{user_subscription_id}/activate',
    status_code=HTTPStatus.OK,
    summary='Активация подписки',
    responses={
        HTTPStatus.BAD_REQUEST: {'model': HttpExceptionModel},
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
    },
)
@check_access({Roles.admin})
async def activate_user_subscription(
        user_subscription_id: UUID,
        user_subscription_service: MeUserSubscriptionService = Depends(get_me_user_subscription_service),
        user: dict = Depends(security_jwt),
) -> None:
    await user_subscription_service.activate_subscription(user_subscription_id)


@router.post(
    '/{user_subscription_id}/cancel',
    status_code=HTTPStatus.OK,
    summary='Приостановка подписки',
    responses={
        HTTPStatus.BAD_REQUEST: {'model': HttpExceptionModel},
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
    },
)
@check_access({Roles.admin})
async def cancel_user_subscription(
        user_subscription_id: UUID,
        user_subscription_service: MeUserSubscriptionService = Depends(get_me_user_subscription_service),
        user: dict = Depends(security_jwt),
) -> None:
    await user_subscription_service.cancel_subscription(user_subscription_id)


@router.post(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    summary='Получение подписок пользователя',
    responses={
        HTTPStatus.BAD_REQUEST: {'model': HttpExceptionModel},
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
    },
)
@check_access({Roles.admin})
async def cancel_user_subscription(
        user_subscription_id: UUID,
        user_subscription_service: MeUserSubscriptionService = Depends(get_me_user_subscription_service),
        user: dict = Depends(security_jwt),
) -> None:
    await user_subscription_service.cancel_subscription(user_subscription_id)

