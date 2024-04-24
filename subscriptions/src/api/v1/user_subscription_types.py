from http import HTTPStatus

from fastapi import APIRouter, Depends

from schemas.error import HttpExceptionModel
from schemas.subscription_type import SubscriptionTypeResponse
from services.access import Roles, check_access, security_jwt
from services.subscription_type import SubscriptionTypeService, get_subscription_type_service

router = APIRouter(redirect_slashes=False, prefix="/user-subscription-types", tags=["Subscription types for user"])


@router.get(
    "",
    response_model=list[SubscriptionTypeResponse],
    summary="Получение списка типов подписок на текущую дату, доступен пользователю",
    responses={
        HTTPStatus.UNAUTHORIZED: {"model": HttpExceptionModel},
        HTTPStatus.FORBIDDEN: {"model": HttpExceptionModel},
    },
)
@check_access({Roles.user})
async def list_current_subscriptions(
    subscription_type_service: SubscriptionTypeService = Depends(get_subscription_type_service),
    user: dict = Depends(security_jwt),
) -> list[SubscriptionTypeResponse]:
    return await subscription_type_service.list_current_subscription_types()
