from http import HTTPStatus
from typing import Any
from urllib.error import URLError

from sendgrid.helpers.mail import From, HtmlContent, Mail, SendAt, Subject
from src.core.config import settings
from src.core.logger import logger
from src.schemas.email import EmailNotification
from src.services.base import AbstractService
from src.utils.get_datetime import get_send_datetime


class SendgridService(AbstractService):
    async def send(self, notice: EmailNotification) -> dict[str, Any]:
        """Отправка сообщения по почте."""
        message = Mail(
            from_email=From(settings.email.from_email),
            to_emails=notice.message_to_email,
            subject=Subject(notice.message_subject),
            html_content=HtmlContent(notice.message_body),
        )

        if not notice.is_priority:
            # проверяем на разрешенное время отправки и
            send_datetime = await get_send_datetime(notice.user_timezone)
            message.send_at = SendAt(send_at=int(send_datetime.timestamp()))

        logger.debug(f"Сформированно сообщение {message.get()}")

        if settings.app.debug or settings.email.api_sendgrid == "default":
            return {"detail": "Success"}

        try:
            response = self.sendgrid_client.connect.send(message=message)
        except (URLError, Exception):  # noqa
            logger.exception(f"Ошибка при отправке email: {notice}")
            return {"detail": "Failure", **self.check_to_resend(notice)}

        if response.status_code != HTTPStatus.ACCEPTED:
            logger.error(f"Неудачная отправка - status {response.status_code} | email: {notice}")
            return {"detail": "Failure", **self.check_to_resend(notice)}

        logger.debug(f"Успешная отправка  - status {response.status_code} | email: {notice}")

        return {"detail": "Success"}
