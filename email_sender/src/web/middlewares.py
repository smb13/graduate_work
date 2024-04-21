import logging
import time
from collections.abc import Callable
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from src.core.config import settings
from src.core.logger import logger


class Middleware:
    @staticmethod
    async def exceptions_middleware(request: Request, call_next: Callable) -> Callable:
        """
        Обработчик исключений и статус кодов.
        """
        try:
            return await call_next(request)
        except Exception as exc:  # noqa: BLE001 - в данном случае отлавливаем все ошибки
            data = {
                "method": request.method,
                "url": str(request.url.path),
                "error": repr(exc),
            }
            message = " ".join(f"{k}: {v}" for k, v in data.items())
            logger.exception(message)
            return ORJSONResponse(
                content={"detail": repr(exc)},
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )

    @staticmethod
    async def log_requests_with_time(request: Request, call_next: Callable) -> Callable:
        """Дополнительный замер времени запроса."""
        start_time = time.monotonic()
        response = await call_next(request)
        process_time = (time.monotonic() - start_time) * 1000
        formatted_process_time = f"{process_time:.2f}"
        client_ip = request.headers.get("X-Client-Ip")

        if (
            request.url.path.endswith("liveness-probe") is False
            and request.url.path.endswith("readiness-probe") is False
        ):
            logger.debug(
                f"{client_ip if client_ip else request.client.host} - "
                f"{request.method} {request.url.path} - "
                f"{formatted_process_time}ms - "
                f"{response.status_code}",
            )

        return response

    def setup_middlewares(self, app: FastAPI) -> None:
        """Применение всех middleware."""

        app.add_middleware(
            CORSMiddleware,  # noqa
            allow_origins=settings.app.allow_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        if settings.app.log_level < logging.INFO:
            app.middleware("http")(self.log_requests_with_time)
        app.middleware("http")(self.exceptions_middleware)
