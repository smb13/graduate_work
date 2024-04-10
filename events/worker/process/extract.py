from collections.abc import Generator

import backoff
from process.decorator import coroutine
from process.load import ModelsSchemas

from core.config import rabbitmq_settings
from core.logger import logger

consuming_messages = []


class RabbitMQExtractor:
    @coroutine
    @backoff.on_exception(**rabbitmq_settings.get_backoff_settings())
    def run(
        self,
        next_node: Generator,
    ) -> Generator[None, list[dict[str, str | ModelsSchemas]], None]:
        while True:
            messages = yield

            logger.info(f"{len(messages)} messages was consumed from RabbitMQ and was send to transformation ...")
            next_node.send(messages)
