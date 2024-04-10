from collections.abc import Generator

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
    @coroutine
    @backoff.on_exception(backoff.expo, Exception, logger=logger, max_tries=settings.backoff_max_tries)
    def run(
        self,
        next_node: Generator,
    ) -> Generator[None, list[dict[str, str | ModelsSchemas]], None]:
        while rmq_messages := (yield):  # type: ignore
            notification_messages = []
            logger.info("Start data transformation ...")
            events_admin_request = EventsAdminRequest()
            auth_request = AuthRequest()
            for rmq_message in rmq_messages:
                message = rmq_message.get("message").message
                rmq_message.get("delivery_tag")

                match rmq_message.get("type"):
                    case RmqQueue.PUSH_REVIEW_LIKE.value | RmqQueue.PUSH_GENERAL_NOTICE.value:
                        _type = ChannelType.PUSH
                    case RmqQueue.EMAIL_WEEKLY_BOOKMARKS.value | RmqQueue.EMAIL_GENERAL_NOTICE.value:
                        _type = ChannelType.EMAIL
                    case _:
                        continue

                notification_id = message.notification_id

                text = message.text

                subject = message.subject
                try:
                    user_id = message.user_id
                except Exception:
                    user_id = None

                users_data = []
                # если user_id непустой, то отправка одному пользователю
                if user_id:
                    try:
                        email, first_name, last_name = auth_request.get_user_details(user_id=user_id)
                        users_data.append(
                            {
                                "user_id": user_id,
                                "email": email,
                                "first_name": first_name,
                                "last_name": last_name,
                            },
                        )
                    except Exception as exc:
                        logger.warning(exc)
                        continue
                else:
                    try:
                        user_ids = events_admin_request.get_subscribers()
                    except requests.exceptions.RequestException:
                        continue
                    try:
                        for user_id in user_ids:
                            email, first_name, last_name = auth_request.get_user_details(user_id=user_id)
                            users_data.append(
                                {
                                    "user_id": user_id,
                                    "email": email,
                                    "first_name": first_name,
                                    "last_name": last_name,
                                },
                            )
                    except Exception as exc:
                        logger.warning(exc)
                        continue
                template_id = message.template_id
                if template_id:
                    try:
                        template = events_admin_request.get_template(template_id=template_id)
                    except requests.exceptions.RequestException:
                        template = events_admin_request.get_default_template()
                else:
                    template = events_admin_request.get_default_template()
                jinja_template = jinja_env.from_string(template)
                # есть ли в шаблоне поля, если есть, то сообщение персонифицировано, если нет, то нет
                template_variables = jinja2.meta.find_undeclared_variables(jinja_env.parse(template))
                to = []
                # формируем не персонифицированное сообщение
                if (len(template_variables) == 1) and ("text" in template_variables):
                    try:
                        body = jinja_template.render(text=text)
                    except Exception as exc:
                        logger.warning(exc)
                        continue
                    if _type == ChannelType.PUSH:
                        for user_data in users_data:
                            to.append(user_data.get("user_id"))
                    else:
                        for user_data in users_data:
                            to.append(user_data.get("email"))
                    match _type:
                        case ChannelType.PUSH:
                            notification_message = PushNotificationModel(
                                notification_id=notification_id,
                                subject=subject,
                                to=to,
                                body=body,
                            )
                        case ChannelType.EMAIL:
                            notification_message = EmailNotificationModel(
                                notification_id=notification_id,
                                subject=subject,
                                to=to,
                                body=body,
                            )
                        case _:
                            continue
                    notification_messages.append(
                        {
                            "type": _type,
                            "delivery_tag": rmq_message.get("delivery_tag"),
                            "headers": message.get("message").headers,
                            "message": notification_message,
                        },
                    )
                # формируем персонифицированные сообщения
                else:
                    try:
                        for user_data in users_data:
                            body = jinja_template.render(
                                first_name=user_data.get("first_name"),
                                last_name=user_data.get("last_name"),
                                text=text,
                            )
                            match _type:
                                case ChannelType.PUSH:
                                    notification_message = PushNotificationModel(
                                        notification_id=notification_id,
                                        subject=subject,
                                        to=[user_data.get("user_id")],
                                        body=body,
                                    )
                                case ChannelType.EMAIL:
                                    notification_message = EmailNotificationModel(
                                        notification_id=notification_id,
                                        subject=subject,
                                        to=[user_data.get("email")],
                                        body=body,
                                    )
                                case _:
                                    raise Exception("Ошибка создания сообщения")
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
            logger.info(
                f"{len(rmq_messages)} messages was transformed to {len(notification_messages)} and "
                + "was send to load to notification service...",
            )
            next_node.send(notification_messages)
