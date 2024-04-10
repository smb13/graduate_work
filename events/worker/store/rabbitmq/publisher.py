import threading

import backoff
from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from pika.delivery_mode import DeliveryMode
from pika.exceptions import AMQPConnectionError, AMQPError
from pika.exchange_type import ExchangeType
from pika.spec import BasicProperties

from core.config import rabbitmq_settings
from core.logger import logger


class RabbitMQPublisher(threading.Thread):
    def __init__(self, queue: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_running = True
        self.exchange = rabbitmq_settings.publish_exchange
        self.message_ttl = rabbitmq_settings.message_ttl
        self.queue = queue
        self.connection = None
        self.channel = None
        self.params = ConnectionParameters(
            host=rabbitmq_settings.host,
            port=rabbitmq_settings.port,
            virtual_host=rabbitmq_settings.virtual_host,
            credentials=PlainCredentials(
                username=rabbitmq_settings.username,
                password=rabbitmq_settings.password,
            ),
        )

    @backoff.on_exception(logger=logger, **rabbitmq_settings.get_backoff_settings())
    def connect(self):
        self.connection = BlockingConnection(parameters=self.params)
        self.channel = self.connection.channel()
        self.channel.exchange_declare(
            exchange=self.exchange,
            exchange_type=ExchangeType.direct,
            passive=False,
            durable=True,
            auto_delete=False,
        )
        self.channel.queue_declare(queue=self.queue, durable=True, arguments={"x-message-ttl": self.message_ttl})
        self.channel.queue_bind(
            queue=self.queue,
            exchange=self.exchange,
            routing_key=self.queue,
        )

    def run(self):
        self.connect()
        while self.is_running:
            try:
                self.connection.process_data_events(time_limit=10)
            except AMQPError as err:
                logger.warning(err)
                self.connect()

    @backoff.on_exception(logger=logger, **rabbitmq_settings.get_backoff_settings())
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
        except AMQPConnectionError as err:
            logger.warning(err)
            self.connect()
            raise AMQPError

    def publish(self, message: str, x_request_id: str):
        self.connection.add_callback_threadsafe(
            lambda: self._publish(
                routing_key=self.queue,
                message=message,
                x_request_id=x_request_id,
            ),
        )

    def stop(self):
        self.is_running = False
        self.connection.process_data_events(time_limit=0)
        if self.connection.is_open:
            self.connection.close()


rmq_publisher: RabbitMQPublisher | None = None


def get_publisher() -> RabbitMQPublisher:
    return rmq_publisher
