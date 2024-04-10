import json

import websockets
from aio_pika.abc import AbstractIncomingMessage
from pydantic import ValidationError
from src.core.logger import logger
from src.models.notifications import WebSocketNotification
from src.utils.decode_jwt import decode_jwt_and_get_userid
from websockets.server import WebSocketServerProtocol

ws_connT: dict[str, websockets.server.WebSocketServerProtocol] = {}


async def handler(ws: WebSocketServerProtocol):
    """Обработчик websocket."""
    jwt_token = json.loads(await ws.recv())
    if (user_id := await decode_jwt_and_get_userid(jwt_token.get("jwt_token"))) is None:
        await ws.close(1011, "Некорректный JWT токен")
        return

    ws_connT[user_id] = ws
    logger.warning("Пользователь подключен %s", user_id)
    try:
        await ws.wait_closed()
    finally:
        del ws_connT[user_id]
        logger.warning("Пользователь отключен %s", user_id)


async def send_by_websocket(message: AbstractIncomingMessage) -> None:
    """Отправка сообщения по websocket."""
    try:
        notification = WebSocketNotification.parse_raw(message.body)
    except ValidationError:
        logger.exception("Ошибка при обработке данных по ws: %s", message.body)
        return

    if (ws := ws_connT.get(str(notification.user_id))) is not None:
        await ws.send(notification.msg_body)
