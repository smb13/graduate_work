import threading
from enum import Enum

import backoff
from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from pika.delivery_mode import DeliveryMode
from pika.exceptions import AMQPConnectionError, AMQPError
from pika.spec import BasicProperties

from core.config import rabbitmq_settings
from schemas.requests import ChannelType


class Actions(Enum):
    REVIEW_LIKE = "review_like"
    WEEKLY_BOOKMARKS = "weekly_bookmarks"
    GENERAL_NOTICE = "general_notice"


def get_rmq_queues_list():
    return [
        ChannelType.PUSH.value + "." + Actions.REVIEW_LIKE.value,
        ChannelType.EMAIL.value + "." + Actions.WEEKLY_BOOKMARKS.value,
        ChannelType.PUSH.value + "." + Actions.GENERAL_NOTICE.value,
        ChannelType.EMAIL.value + "." + Actions.GENERAL_NOTICE.value,
    ]


class RmqPublisher(threading.Thread):
    def __init__(
        self,
        exchange: str,
        queues: list,
        host: str,
        port: str,
        username: str,
        password: str,
        virtual_host: str,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.is_running = True
        self.exchange = exchange
        self.queues = queues
        self.connection = None
        self.channel = None
        self.params = ConnectionParameters(
            host=host,
            port=port,
            virtual_host=virtual_host,
            credentials=PlainCredentials(
                username=username,
                password=password,
            ),
        )

    @backoff.on_exception(**rabbitmq_settings.get_backoff_settings())
    def connect(self):
        self.connection = BlockingConnection(parameters=self.params)
        self.channel = self.connection.channel()
        for queue in self.queues:
            self.channel.queue_declare(queue=queue, durable=True)

    def run(self):
        self.connect()
        while self.is_running:
            try:
                self.connection.process_data_events(time_limit=1)
            except AMQPError:
                self.connect()

    @backoff.on_exception(**rabbitmq_settings.get_backoff_settings())
    def _publish(self, routing_key: str, message: str, x_request_id: str):
        try:
            self.channel.basic_publish(
                exchange=self.exchange,
                routing_key=routing_key,
                body=message,
                properties=BasicProperties(
                    content_type="application/json",
                    delivery_mode=DeliveryMode.Persistent,
                    headers={"X-Request-Id": x_request_id},
                ),
                mandatory=True,
            )
        except AMQPConnectionError:
            self.connect()
            raise AMQPError

    def publish(self, routing_key: str, message: str, x_request_id: str):
        self.connection.add_callback_threadsafe(
            lambda: self._publish(
                routing_key=routing_key,
                message=message,
                x_request_id=x_request_id,
            ),
        )

    def stop(self):
        self.is_running = False
        self.connection.process_data_events(time_limit=1)
        if self.connection.is_open:
            self.connection.close()


rmq_publisher: RmqPublisher | None = None


async def get_publishers() -> RmqPublisher:
    return rmq_publisher
