import logging
from contextlib import asynccontextmanager

import uvicorn
from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette.requests import Request
from starlette.responses import JSONResponse

from api.v1 import subscription_types, user_subscriptions

from core.config import project_settings
from core.logger import LOGGING


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


@AuthJWT.load_config
def get_config():
    return project_settings


app = FastAPI(
    # Название проекта, используемое в документации.
    title=project_settings.name,
    # Адрес документации (swagger).
    docs_url='/api/openapi',
    # Адрес документации (openapi).
    openapi_url='/api/openapi.json',
    # Оптимизация работы с JSON-сериализатором.
    default_response_class=ORJSONResponse,
    # Указываем функцию, обработки жизненного цикла приложения.
    lifespan=lifespan,
    # Описание сервиса
    description="API для сайта, личного кабинета и управления доступами",
)

# Подключаем роутер к серверу с указанием префикса для API (/v1/films).
app.include_router(subscription_types.router, prefix='/api/v1')
app.include_router(user_subscriptions.router, prefix='/api/v1')


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(_: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


if __name__ == '__main__':
    # Запускаем приложение с помощью uvicorn сервера.
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )
