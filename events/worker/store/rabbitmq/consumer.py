import functools
import json
import threading
from typing import Any

import backoff
import pika
from pika.exceptions import AMQPError
from pika.exchange_type import ExchangeType
from store.models import (
    GeneralNoticeMessage,
    GeneralNoticeModel,
    ReviewLikeMessage,
    ReviewLikeModel,
    WeeklyBookmarksMessage,
    WeeklyBookmarksModel,
)
from store.rabbitmq.queues import RmqQueue

from core.config import rabbitmq_settings
from core.logger import logger


class RabbitMQConsumer(threading.Thread):
    def __init__(self, queue: str, routing_key: str, consuming_messages: list[dict[str, str | Any]], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel = None
        self.connection = None
        self.result = consuming_messages
        self.queue = queue
        self.routing_key = routing_key

    @backoff.on_exception(logger=logger, **rabbitmq_settings.get_backoff_settings())
    def connect(self):
        try:
            credentials = pika.PlainCredentials(rabbitmq_settings.username, rabbitmq_settings.password)
            parameters = pika.ConnectionParameters(
                host=rabbitmq_settings.host,
                port=rabbitmq_settings.port,
                credentials=credentials,
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            self.channel.exchange_declare(
                exchange=rabbitmq_settings.consume_exchange,
                exchange_type=ExchangeType.direct,
                passive=False,
                durable=True,
                auto_delete=False,
            )
            self.channel.queue_declare(queue=self.queue, durable=True)
            self.channel.queue_bind(
                queue=self.queue,
                exchange=rabbitmq_settings.consume_exchange,
                routing_key=self.routing_key,
            )
            self.channel.basic_qos(prefetch_count=rabbitmq_settings.prefetch_count)

            on_message_callback = functools.partial(self.on_message)
            self.channel.basic_consume(queue=self.queue, on_message_callback=on_message_callback)
            return self
        except AMQPError as err:
            logger.warning(err)
            if self.connection:
                self.connection.close()
            raise AMQPError

    @backoff.on_exception(logger=logger, **rabbitmq_settings.get_backoff_settings())
    def run(self):
        self.connect()
        self.channel.start_consuming()
        self.channel.stop_consuming()

    def stop(self):
        if self.connection:
            self.connection.close()

    def on_message(self, chan, method_frame, header_frame, body):
        match self.queue:
            case RmqQueue.PUSH_REVIEW_LIKE.value:
                message = ReviewLikeModel(
                    headers=header_frame.headers,
                    message=ReviewLikeMessage(**json.loads(body)),
                )
            case RmqQueue.EMAIL_WEEKLY_BOOKMARKS.value:
                message = WeeklyBookmarksModel(
                    headers=header_frame.headers,
                    message=WeeklyBookmarksMessage(**json.loads(body)),
                )
            case RmqQueue.PUSH_GENERAL_NOTICE.value | RmqQueue.EMAIL_GENERAL_NOTICE.value:
                message = GeneralNoticeModel(
                    headers=header_frame.headers,
                    message=GeneralNoticeMessage(**json.loads(body)),
                )
            case _:
                return
        self.result.append({"type": self.queue, "message": message, "delivery_tag": method_frame.delivery_tag})

    @backoff.on_exception(logger=logger, **rabbitmq_settings.get_backoff_settings())
    def message_ack(self, delivery_tag: int):
        try:
            self.channel.basic_ack(delivery_tag=delivery_tag)
        except AMQPError as err:
            logger.warning(err)
            self.connect()
            raise AMQPError
