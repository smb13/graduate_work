import uuid
from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Path, Query

from core.config import settings
from schemas.notifications import EmailNotification, PushNotification, PushNotificationsListResponse
from services.notifications import NotificationsService, get_notifications_service

router = APIRouter(redirect_slashes=False)


@router.post(
    path="/email",
    summary="Отправка email нотификации",
    status_code=HTTPStatus.CREATED,
)
async def send_email_notification(
    request: EmailNotification = Body(...),
    notifications_service: NotificationsService = Depends(get_notifications_service),
) -> None:
    await notifications_service.send_email_notification(request)


@router.post(
    path="/push",
    summary="Отправка push нотификации",
    status_code=HTTPStatus.CREATED,
)
async def send_push_notification(
    request: PushNotification = Body(...),
    notifications_service: NotificationsService = Depends(get_notifications_service),
) -> None:
    await notifications_service.send_push_notification(request)


@router.post(
    path="/push/{notification_id}",
    summary="Отметка уведомления как прочитанного",
    status_code=HTTPStatus.OK,
)
async def mark_notification_as_read(
    notification_id: UUID = Path(..., description="Идентификатор уведомления", example=uuid.uuid4()),
    notifications_service: NotificationsService = Depends(get_notifications_service),
) -> None:
    await notifications_service.mark_notification_as_read(notification_id)


@router.get(
    path="/push/{user_id}",
    summary="Получение списка доставленных push уведомлений",
    status_code=HTTPStatus.OK,
)
async def get_notifications_history(
    user_id: str = Path(..., description="Идентификатор пользователя", example="test@test.com"),
    page: int = Query(default=1, description="Pagination page number", ge=1),
    page_size: int = Query(
        default=settings.page_size,
        description="Pagination page size",
        ge=1,
        le=settings.page_size_max,
    ),
    notifications_service: NotificationsService = Depends(get_notifications_service),
) -> PushNotificationsListResponse:
    return await notifications_service.get_notifications_history(user_id, page, page_size)
