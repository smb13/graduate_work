import asyncio

import backoff
from aio_pika import connect
from aiormq import AMQPConnectionError
from src.core.config import settings
from src.core.logger import logger
from src.sendlers.websocket import send_by_websocket


@backoff.on_exception(backoff.expo, AMQPConnectionError, max_tries=settings.app.backoff_max_tries)
async def init_rabbit():
    """Подключение к rabbit mq."""
    connection = await connect(
        host=settings.rabbit.host,
        port=settings.rabbit.port,
        login=settings.rabbit.user,
        password=settings.rabbit.password,
    )
    return connection


async def process_notifications():
    """Отправка сообщения в rabbit."""
    connection = await init_rabbit()
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(settings.websocket.exchange)
        logger.info("Прослушивание очереди %s", settings.websocket.exchange)
        await queue.consume(send_by_websocket, no_ack=True)
        await asyncio.Future()
