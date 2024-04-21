from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from schemas.error import HttpExceptionModel
from schemas.subscription_type import SubscriptionTypeBase, SubscriptionTypeResponse
from services.access import security_jwt, Roles, check_access
from services.subscription_type import SubscriptionTypeService, get_subscription_type_service

router = APIRouter(redirect_slashes=False, prefix="/subscription-types", tags=['Subscription types'])


@router.post(
    '',
    response_model=SubscriptionTypeResponse,
    summary='Создание типа подписки, доступен администратору',
    status_code=HTTPStatus.CREATED,
    responses={
        HTTPStatus.BAD_REQUEST: {'model': HttpExceptionModel},
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
    },
)
@check_access({Roles.admin})
async def create_subscription_type(
        subscription_type: SubscriptionTypeBase,
        subscription_type_service: SubscriptionTypeService = Depends(get_subscription_type_service),
        user: dict = Depends(security_jwt),
) -> SubscriptionTypeResponse:
    return await subscription_type_service.create_subscription_type(subscription_type)


@router.patch(
    '/{subscription_type_id}',
    response_model=SubscriptionTypeResponse,
    summary='Изменение типа подписки, доступен администратору',
    status_code=HTTPStatus.OK,
    responses={
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
        HTTPStatus.NOT_FOUND: {'model': HttpExceptionModel},
    },
)
@check_access({Roles.admin})
async def patch_subscription_type(
        subscription_type_id: int,
        subscription_type_patch: SubscriptionTypeBase,
        subscription_type_service: SubscriptionTypeService = Depends(get_subscription_type_service),
        user: dict = Depends(security_jwt),
) -> SubscriptionTypeResponse:
    subscription_type = await subscription_type_service.patch_subscription_type(subscription_type_id,
                                                                                subscription_type_patch)
    if not subscription_type:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Subscription type not found')
    return subscription_type


@router.get(
    '/{subscription_type_id}',
    status_code=HTTPStatus.OK,
    summary='Получение типа подписки по id, доступен администратору и пользователю',
    responses={
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
        HTTPStatus.NOT_FOUND: {'model': HttpExceptionModel},
    },
)
@check_access({Roles.user, Roles.admin})
async def get_subscription_type_by_id(
        subscription_type_id: int,
        subscription_type_service: SubscriptionTypeService = Depends(get_subscription_type_service),
        user: dict = Depends(security_jwt),
) -> SubscriptionTypeResponse:
    subscription_type = await subscription_type_service.get_subscription_type_by_id(subscription_type_id)
    if not subscription_type:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Subscription type not found')
    return subscription_type


@router.get(
    '',
    response_model=list[SubscriptionTypeResponse],
    summary='Получение списка всех, в том числе недействующих на текущую дату, типов подписок, доступен администратору',
    responses={
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
    },
)
@check_access({Roles.admin})
async def list_all_subscriptions(
        subscription_type_service: SubscriptionTypeService = Depends(get_subscription_type_service),
        user: dict = Depends(security_jwt),
) -> list[SubscriptionTypeResponse]:
    return await subscription_type_service.mock_list_all_subscription_types()
