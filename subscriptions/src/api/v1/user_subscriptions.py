from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer

from schemas.error import HttpExceptionModel
from schemas.user_subscription import UserSubscriptionResponse, UserSubscriptionBase
from services.user_subscription import UserSubscriptionService, get_user_subscription_service

router = APIRouter(redirect_slashes=False, prefix="/user_subscriptions", tags=['User subscriptions'])


@router.post(
    '',
    response_model=UserSubscriptionResponse,
    summary='Создание подписки пользователя',
    status_code=HTTPStatus.CREATED,
    responses={
        HTTPStatus.BAD_REQUEST: {'model': HttpExceptionModel},
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
    },
    dependencies=[Depends(HTTPBearer())]
)
# @check_access('admin')
async def create_user_subscription(
        user_subscription: UserSubscriptionBase,
        user_subscription_service: UserSubscriptionService = Depends(get_user_subscription_service),
) -> UserSubscriptionResponse:
    return await user_subscription_service.create_user_subscription(user_subscription)


@router.patch(
    '/{role_id}',
    response_model=UserSubscriptionResponse,
    summary='Изменение подписки пользователя',
    status_code=HTTPStatus.OK,
    responses={
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
        HTTPStatus.NOT_FOUND: {'model': HttpExceptionModel},
    },
    dependencies=[Depends(HTTPBearer())]
)
# @check_access('admin')
async def patch_role(
        user_subscription_id: UUID,
        user_subscription_patch: UserSubscriptionBase,
        user_subscription_service: UserSubscriptionService = Depends(get_user_subscription_service),
) -> UserSubscriptionResponse:
    user_subscription = await user_subscription_service.patch_user_subscription(user_subscription_id,
                                                                                user_subscription_patch)
    if not user_subscription:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Subscription type not found')
    return user_subscription


@router.get(
    '',
    response_model=list[UserSubscriptionResponse],
    summary='Получение списка подписок пользователя',
    responses={
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
    },
    dependencies=[Depends(HTTPBearer())]
)
# @check_access(role_management)
async def list_roles(
        user_subscription_service: UserSubscriptionService = Depends(get_user_subscription_service),
) -> list[UserSubscriptionResponse]:
    return await user_subscription_service.list_user_subscriptions()


@router.post(
    '/{user_subscription_id}/activate',
    status_code=HTTPStatus.CREATED,
    summary='Активация подписки',
    responses={
        HTTPStatus.BAD_REQUEST: {'model': HttpExceptionModel},
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
    },
    dependencies=[Depends(HTTPBearer())]
)
# @check_access(role_management)
async def activate_user_subscription(
        user_subscription_id: UUID,
        user_subscription_service: UserSubscriptionService = Depends(get_user_subscription_service),
) -> None:
    await user_subscription_service.activate_subscription(user_subscription_id)


@router.post(
    '/{user_subscription_id}/cancel',
    status_code=HTTPStatus.CREATED,
    summary='Приостановка подписки',
    responses={
        HTTPStatus.BAD_REQUEST: {'model': HttpExceptionModel},
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
    },
    dependencies=[Depends(HTTPBearer())]
)
# @check_access(role_management)
async def cancel_user_subscription(
        user_subscription_id: UUID,
        user_subscription_service: UserSubscriptionService = Depends(get_user_subscription_service),
) -> None:
    await user_subscription_service.cancel_subscription(user_subscription_id)

