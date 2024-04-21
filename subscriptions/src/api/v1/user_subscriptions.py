from http import HTTPStatus
from typing_extensions import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from schemas.error import HttpExceptionModel
from schemas.user_subscription import UserSubscriptionResponse
from services.access import security_jwt, check_access, Roles
from services.user_subscription import UserSubscriptionService, get_user_subscription_service

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
        payment_method_id: UUID,
        user_subscription_service: UserSubscriptionService = Depends(get_user_subscription_service),
        user: dict = Depends(security_jwt),
) -> None:
    await user_subscription_service.activate_subscription(user_subscription_id=user_subscription_id,
                                                          payment_method_id=payment_method_id)


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
        user_subscription_service: UserSubscriptionService = Depends(get_user_subscription_service),
        user: dict = Depends(security_jwt),
) -> None:
    await user_subscription_service.cancel_subscription(user_subscription_id)


@router.get(
    '',
    response_model=list[UserSubscriptionResponse],
    summary='Получение списка подписок пользователя',
    responses={
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
    },
)
@check_access({Roles.admin})
async def get_user_active_subscriptions(
        user_id: Annotated[UUID, Query(description="User id")],
        subscription_type_id: Annotated[int, Query(description="Subscription type id")] = None,
        user_subscription_service: UserSubscriptionService = Depends(get_user_subscription_service),
        user: dict = Depends(security_jwt),
) -> list[UserSubscriptionResponse]:
    return await user_subscription_service.list_user_active_subscriptions(user_id=user_id,
                                                                          subscription_type_id=subscription_type_id)

