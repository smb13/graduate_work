from http import HTTPStatus
from urllib.error import URLError

from sendgrid.helpers.mail import From, HtmlContent, Mail, SendAt, Subject
from src.core.config import settings
from src.core.logger import logger
from src.schemas import base as base_schemas
from src.schemas.email import EmailNotification, ResponseEmailNotification
from src.services.base import AbstractService
from src.utils.get_datetime import get_send_datetime


class SendgridService(AbstractService):
    async def send(self, notice: EmailNotification) -> base_schemas.ResponseBase | ResponseEmailNotification:
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
            return base_schemas.ResponseBase(detail="Success")
        try:
            response = self.sendgrid_client.connect.send(message=message)
        except (URLError, Exception):  # noqa
            logger.exception(f"Ошибка при отправке email: {notice}")
            if response_resend := self.check_to_resend(notice):
                return ResponseEmailNotification(detail="Failure", **response_resend.dict())
            return base_schemas.ResponseBase(detail="The number of attempts has ended")

        if response.status_code != HTTPStatus.ACCEPTED:
            logger.error(f"Неудачная отправка - status {response.status_code} | email: {notice}")
            if response_resend := self.check_to_resend(notice):
                return ResponseEmailNotification(detail="Failure", **response_resend.dict())
            return base_schemas.ResponseBase(detail="The number of attempts has ended")

        logger.debug(f"Успешная отправка  - status {response.status_code} | email: {notice}")

        return base_schemas.ResponseBase(detail="Success")
