from http import HTTPStatus

from fastapi import APIRouter, Depends
from src.schemas import base as base_schemas
from src.schemas.email import EmailNotification, ResponseEmailNotification
from src.services.senders import SendgridService

router = APIRouter()


@router.get(
    path="/liveness-probe",
    tags=["Health Check"],
    summary="Проверка состояния сервиса",
    description="Проверяет доступность сервиса",
    response_model=base_schemas.ResponseBase,
)
async def liveness() -> base_schemas.ResponseBase:
    return base_schemas.ResponseBase(detail="pong")


@router.post(
    path="/send-email",
    tags=["Email"],
    summary="Отправка email",
    description="Отправляет email согласно заданным требованиям",
    responses={
        HTTPStatus.BAD_REQUEST: {"model": base_schemas.ResponseBase},
    },
)
async def post_status(
    json_params: EmailNotification,
    email_service: SendgridService = Depends(SendgridService.get_service),
) -> base_schemas.ResponseBase | ResponseEmailNotification:
    return await email_service.send(json_params)
