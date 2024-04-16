from datetime import date
from http import HTTPStatus
from typing_extensions import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query
from fastapi.security import HTTPBearer

from schemas.error import HttpExceptionModel
from schemas.subscription_type import SubscriptionTypeBase, SubscriptionTypeResponse
from services.subscription_type import check_access, SubscriptionTypeService, get_subscription_type_service

router = APIRouter(redirect_slashes=False, prefix="/subscription-types", tags=['Subscription types'])


@router.post(
    '',
    response_model=SubscriptionTypeResponse,
    summary='Создание типа подписки',
    status_code=HTTPStatus.CREATED,
    responses={
        HTTPStatus.BAD_REQUEST: {'model': HttpExceptionModel},
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
    },
    dependencies=[Depends(HTTPBearer())]
)
# @check_access('admin')
async def create_subscription_type(
        subscription_type: SubscriptionTypeBase,
        subscription_type_service: SubscriptionTypeService = Depends(get_subscription_type_service),
) -> SubscriptionTypeResponse:
    return await subscription_type_service.create_subscription_type(subscription_type)


@router.patch(
    '/{role_id}',
    response_model=SubscriptionTypeResponse,
    summary='Изменение типа подписки',
    status_code=HTTPStatus.OK,
    responses={
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
        HTTPStatus.NOT_FOUND: {'model': HttpExceptionModel},
    },
    dependencies=[Depends(HTTPBearer())]
)
# @check_access('admin')
async def patch_subscription_type(
        subscription_type_id: UUID,
        subscription_type_patch: SubscriptionTypeBase,
        subscription_type_service: SubscriptionTypeService = Depends(get_subscription_type_service),
) -> SubscriptionTypeResponse:
    subscription_type = await subscription_type_service.patch_subscription_type(subscription_type_id,
                                                                                subscription_type_patch)
    if not subscription_type:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Subscription type not found')
    return subscription_type


@router.get(
    '/{subscription_type_id}',
    status_code=HTTPStatus.NO_CONTENT,
    summary='Удаление типа подписки',
    responses={
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
        HTTPStatus.NOT_FOUND: {'model': HttpExceptionModel},
    },
    dependencies=[Depends(HTTPBearer())]
)
# @check_access('admin')
async def get_subscription_type_by_id(
        subscription_type_id: UUID,
        subscription_type_service: SubscriptionTypeService = Depends(get_subscription_type_service),
) -> None:
    if not (await subscription_type_service.get_subscription_type_by_id(subscription_type_id)):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Subscription type not found')


@router.get(
    '',
    response_model=list[SubscriptionTypeResponse],
    summary='Получение списка ролей',
    responses={
        HTTPStatus.UNAUTHORIZED: {'model': HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {'model': HttpExceptionModel},
    },
    dependencies=[Depends(HTTPBearer())]
)
async def list_roles(
        on_date: Annotated[date, Query(description='Фильтр по дате действия', examples=[date.today(),])] = None,
        subscription_type_service: SubscriptionTypeService = Depends(get_subscription_type_service),
) -> list[SubscriptionTypeResponse]:
    return await subscription_type_service.list_subscription_types(on_date=on_date)

