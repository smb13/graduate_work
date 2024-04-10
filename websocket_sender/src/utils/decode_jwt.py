import jwt
from src.core.config import settings


async def decode_jwt_and_get_userid(token: str) -> str | None:
    """Декодирует  получаемый токен и возвращает user_id."""
    try:
        decoded_token = jwt.decode(token, settings.app.jwt_secret, algorithms=["HS256"])

    except jwt.PyJWTError:
        return None
    return decoded_token["sub"]
