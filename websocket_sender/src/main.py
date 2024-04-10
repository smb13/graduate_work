import asyncio

import websockets
from src.core.config import settings
from src.core.logger import logger
from src.sendlers.rabbit import process_notifications
from src.sendlers.websocket import handler


async def main():
    """Точка запуска приложения."""
    async with websockets.serve(handler, settings.websocket.host, settings.websocket.port):
        logger.info("Старт вебсокета на %s:%s", settings.websocket.host, settings.websocket.port)
        await process_notifications()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Ручное завершение работы приложения")
