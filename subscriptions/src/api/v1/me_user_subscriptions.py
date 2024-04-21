from http import HTTPStatus
from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, Depends

from models import UserSubscription
from schemas.error import HttpExceptionModel
from schemas.user_subscription import UserSubscriptionResponse, UrlResponse
from services.access import security_jwt, check_access, Roles
from services.me_user_subscription import MeUserSubscriptionService, get_me_user_subscription_service

router = APIRouter(redirect_slashes=False, prefix="/me/user_subscriptions", tags=['User subscriptions'])


@router.post(
    '',
    response_model=UrlResponse,
    summary='Пользователь подписывается',
    status_code=HTTPStatus.CREATED,
    responses={
        HTTPStatus.BAD_REQUEST: {'model': HttpExceptionModel},
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
    },
)
@check_access({Roles.user})
async def create_user_subscription(
        subscription_type_id: int,
        me_user_subscription_service: MeUserSubscriptionService = Depends(get_me_user_subscription_service),
        user: dict = Depends(security_jwt),
) -> str | Exception:
    return await me_user_subscription_service.create_user_subscription(
        user=user,
        subscription_type_id=subscription_type_id
    )


@router.patch(
    '/{subscription_id}',
    response_model=str,
    summary='Пользователь отменяет подписку',
    status_code=HTTPStatus.OK,
    responses={
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
        HTTPStatus.NOT_FOUND: {'model': HttpExceptionModel},
    },
)
@check_access({Roles.user})
async def cancel_user_subscription(
        user_subscription_id: UUID,
        me_user_subscription_service: MeUserSubscriptionService = Depends(get_me_user_subscription_service),
        user: dict = Depends(security_jwt),
) -> str | Exception:
    return await (me_user_subscription_service.cancel_user_subscription(
        user=user,
        user_subscription_id=user_subscription_id,
    )
    )


@router.get(
    '',
    response_model=list[UserSubscriptionResponse],
    summary='Получение списка подписок пользователя',
    responses={
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
    },
)
@check_access({Roles.user})
async def list_roles(
        me_user_subscription_service: MeUserSubscriptionService = Depends(get_me_user_subscription_service),
        user: dict = Depends(security_jwt),
) -> Sequence[UserSubscription]:
    return await me_user_subscription_service.list_user_subscriptions(user=user)



