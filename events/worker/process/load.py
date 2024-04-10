from collections.abc import Generator

from process.decorator import coroutine
from store import models
from store.rabbitmq.consumer import RabbitMQConsumer
from store.rabbitmq.publisher import RabbitMQPublisher
from typing_extensions import TypeVar

from core.logger import logger

ModelsSchemas = TypeVar("ModelsSchemas", bound=models)


class NotificationLoader:
    @coroutine
    def run(
        self,
        publisher: RabbitMQPublisher,
        consumer: RabbitMQConsumer,
    ) -> Generator[None, tuple[RabbitMQConsumer, RabbitMQPublisher, list[dict[str, str | ModelsSchemas]]], None]:
        while notification_messages := (yield):  # type: ignore
            acked_rmq_messages = []
            mess_counter = 0
            for notification_message in notification_messages:
                try:
                    publisher.publish(
                        message=notification_message.get("message").model_dump_json(),
                        x_request_id=notification_message.get("headers").get("X-Request-Id"),
                    )
                    delivery_tag = notification_message.get("delivery_tag")
                    if delivery_tag not in acked_rmq_messages:
                        consumer.message_ack(delivery_tag)
                        acked_rmq_messages.append(delivery_tag)
                except Exception as exc:
                    logger.debug(exc)
                    continue
                mess_counter += 1
            logger.info(f"{mess_counter} messages was published to sender...")
