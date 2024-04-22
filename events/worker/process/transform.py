from collections.abc import Generator
from typing import Any

import backoff
import jinja2
import requests
from process.decorator import coroutine
from process.load import ModelsSchemas
from store.auth.auth import AuthRequest
from store.events_admin.events_admin import EventsAdminRequest
from store.models import EmailNotificationModel, PushNotificationModel, jinja_env
from store.rabbitmq.queues import ChannelType, RmqQueue

from core.config import settings
from core.logger import logger


class DataTransform:
    """Класс-этапа трансформации данных."""

    @coroutine
    @backoff.on_exception(backoff.expo, Exception, logger=logger, max_tries=settings.backoff_max_tries)
    def run(self, next_node: Generator) -> Generator[None, list[dict[str, str | ModelsSchemas]], None]:
        """Запуск корутины."""

        while rmq_messages := (yield):
            notification_messages: list[dict[str, Any]] = []
            logger.info("Start data transformation ...")
            for rmq_message in rmq_messages:
                self.process_message(rmq_message, notification_messages)
            logger.info(
                f"{len(rmq_messages)} messages was transformed to "
                f"{len(notification_messages)} and was send to load to notification service...",
            )
            next_node.send(notification_messages)

    def process_message(self, rmq_message: ModelsSchemas, notification_messages: list[dict[str, Any]]) -> None:
        """Получение и обработка сообщений."""

        message = rmq_message.get("message").message
        rmq_message.get("delivery_tag")
        _type = self.determine_message_type(rmq_message.get("type"))

        if not _type:
            return

        notification_id, text, subject, user_id = (
            message.notification_id,
            message.text,
            message.subject,
            self.extract_user_id(message),
        )

        auth_request = AuthRequest()
        events_admin_request = EventsAdminRequest()

        users_data = self.fetch_users_data(user_id, auth_request, events_admin_request)
        template = self.retrieve_template(message.template_id, events_admin_request)
        self.generate_notifications(
            _type,
            users_data,
            text,
            template,
            notification_id,
            subject,
            notification_messages,
            rmq_message,
        )

    @staticmethod
    def determine_message_type(message_type: RmqQueue) -> ChannelType | None:
        """Определение типа сообщения."""

        match message_type:  # noqa
            case RmqQueue.PUSH_REVIEW_LIKE.value | RmqQueue.PUSH_GENERAL_NOTICE.value:
                return ChannelType.PUSH
            case RmqQueue.EMAIL_WEEKLY_BOOKMARKS.value | RmqQueue.EMAIL_GENERAL_NOTICE.value:
                return ChannelType.EMAIL
            case _:
                return None

    @staticmethod
    def extract_user_id(message: Any) -> Any | None:
        """Получение ID пользователя."""
        try:
            return message.user_id
        except Exception:  # noqa
            return None

    def fetch_users_data(
        self,
        user_id: Any | None,
        auth_request: AuthRequest,
        events_admin_request: EventsAdminRequest,
    ) -> list[dict[str, Any]]:
        """Формирование данных для отправки."""

        if user_id:
            return self.get_user_details(user_id, auth_request)
        return self.get_subscriber_details(auth_request, events_admin_request)

    @staticmethod
    def get_user_details(user_id: Any, auth_request: AuthRequest) -> list[dict[str, Any]]:
        """Получение информации по пользователю."""

        try:
            email, first_name, last_name = auth_request.get_user_details(user_id=user_id)
            return [
                {
                    "user_id": user_id,
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                },
            ]
        except Exception as exc:
            logger.warning(exc)
            return []

    @staticmethod
    def get_subscriber_details(
        auth_request: AuthRequest,
        events_admin_request: EventsAdminRequest,
    ) -> list[dict[str, Any]]:
        """Получения информации по подпискам."""

        try:
            user_ids = events_admin_request.get_subscribers()
            return [
                {
                    "user_id": user_id,
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                }
                for user_id in user_ids
                for email, first_name, last_name in [auth_request.get_user_details(user_id=user_id)]
            ]
        except requests.exceptions.RequestException as exc:
            logger.warning(exc)
            return []

    @staticmethod
    def retrieve_template(template_id: Any, events_admin_request: EventsAdminRequest) -> jinja2.Template:
        """Применения шаблона к сообщению."""

        try:
            if template_id:
                return events_admin_request.get_template(template_id=template_id)
            return events_admin_request.get_default_template()
        except requests.exceptions.RequestException:
            return events_admin_request.get_default_template()

    def generate_notifications(
        self,
        _type: ChannelType,
        users_data: list[dict[str, Any]],
        text: str,
        template: Any,
        notification_id: Any,
        subject: Any,
        notification_messages: list[dict[str, Any]],
        rmq_message: dict[str, Any | ModelsSchemas],
    ) -> None:
        """Генерация сообщения из полученных данных."""

        jinja_template = jinja_env.from_string(template)
        # есть ли в шаблоне поля, если есть, то сообщение персонифицировано, если нет, то нет
        template_variables = jinja2.meta.find_undeclared_variables(jinja_env.parse(template))

        # формируем не персонифицированное сообщение
        if "text" in template_variables and len(template_variables) == 1:
            self.create_nonpersonalized_notifications(
                _type,
                users_data,
                text,
                jinja_template,
                notification_id,
                subject,
                notification_messages,
                rmq_message,
            )
        else:
            # формируем персонифицированное сообщение
            self.create_personalized_notifications(
                _type,
                users_data,
                text,
                jinja_template,
                notification_id,
                subject,
                notification_messages,
                rmq_message,
            )

    def create_nonpersonalized_notifications(
        self,
        _type: ChannelType,
        users_data: list[dict[str, Any]],
        text: str,
        jinja_template: Any,
        notification_id: Any,
        subject: Any,
        notification_messages: list[dict[str, Any]],
        rmq_message: ModelsSchemas,
    ) -> None:
        """Формирование НЕ персонализированного сообщения."""

        try:
            body = jinja_template.render(text=text)
        except Exception as exc:
            logger.warning(exc)
            return

        to = [user_data.get("email" if _type == ChannelType.EMAIL else "user_id") for user_data in users_data]
        notification_message = self.create_notification_model(_type, notification_id, subject, to, body)
        if notification_message:
            notification_messages.append(
                {
                    "type": _type,
                    "delivery_tag": rmq_message.get("delivery_tag"),
                    "headers": rmq_message.get("message").headers,
                    "message": notification_message,
                },
            )

    def create_personalized_notifications(
        self,
        _type: ChannelType,
        users_data: list[dict[str, Any]],
        text: str,
        jinja_template: Any,
        notification_id: Any,
        subject: Any,
        notification_messages: list[dict[str, Any]],
        rmq_message: ModelsSchemas,
    ) -> None:
        """Формирование персонализированного сообщения."""

        for user_data in users_data:
            try:
                body = jinja_template.render(
                    first_name=user_data.get("first_name"),
                    last_name=user_data.get("last_name"),
                    text=text,
                )
                to = [user_data.get("email" if _type == ChannelType.EMAIL else "user_id")]
                notification_message = self.create_notification_model(_type, notification_id, subject, to, body)
                if notification_message:
                    notification_messages.append(
                        {
                            "type": _type,
                            "delivery_tag": rmq_message.get("delivery_tag"),
                            "headers": rmq_message.get("message").headers,
                            "message": notification_message,
                        },
                    )
            except Exception as exc:
                logger.warning(exc)
                continue

    @staticmethod
    def create_notification_model(
        _type: ChannelType,
        notification_id: Any,
        subject: Any,
        to: list,
        body: Any,
    ) -> ModelsSchemas | None:
        """Инициализация нужной модели сообшения для отправки."""

        match _type:  # noqa
            case ChannelType.PUSH:
                return PushNotificationModel(notification_id=notification_id, subject=subject, to=to, body=body)
            case ChannelType.EMAIL:
                return EmailNotificationModel(notification_id=notification_id, subject=subject, to=to, body=body)
            case _:
                return None
