import asyncio
import json
import logging
import os
from datetime import datetime, timedelta, timezone

from faker import Faker

import jwt
import websockets

logging.basicConfig(
    level=20,
    format='%(asctime)s [%(levelname)s] [in %(filename)s: line %(lineno)d] - "%(message)s"',
    datefmt="[%Y-%m-%d %H:%M:%S %z]",
)

fake = Faker(locale="en_US")

WS_URL = (
    f"ws://{os.getenv('WEBSOCKET_SENDER_HOST')}:{os.getenv('WEBSOCKET_SENDER_PORT')}"
    if bool(
        os.getenv("WEBSOCKET_SENDER_HOST"),
    )
    and bool(os.getenv("WEBSOCKET_SENDER_PORT"))
    else "ws://127.0.0.1:8080"
)

JWT_KEY = os.getenv("JWT_SECRET") if bool(os.getenv("JWT_SECRET")) else "BIG_BIG_SECRET"
USER_UUID = fake.uuid4()


async def encode_jwt_token():
    token = {"sub": str(USER_UUID), "exp": datetime.now(tz=timezone.utc) + timedelta(hours=10)}
    return jwt.encode(token, JWT_KEY, algorithm="HS256")


async def main():
    async with websockets.connect(WS_URL) as websocket:
        token = await encode_jwt_token()
        data_to_send = json.dumps({"jwt_token": token})
        await websocket.send(data_to_send)
        logging.info(f"Connected to {WS_URL}")

        async for message in websocket:
            logging.info(f"Полученное сообщение: {message}")


if __name__ == "__main__":
    asyncio.run(main())
