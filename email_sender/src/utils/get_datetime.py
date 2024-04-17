from datetime import datetime, time, timedelta

import pytz
from src.core.config import settings
from src.core.logger import logger


async def get_send_datetime(
    user_tz: str,
    start_time: time = settings.email.start_time,
    end_time: time = settings.email.stop_time,
) -> datetime:
    """Получить datetime для отложенной отправки email."""
    try:
        user_now_datetime = datetime.now(tz=pytz.timezone(user_tz))
    except pytz.exceptions.UnknownTimeZoneError:
        logger.exception(f"Неверная строка таймзоны: {user_tz}")
        return datetime.utcnow()

    user_now_time = user_now_datetime.time()

    if user_now_time < start_time:
        time_to_send = timedelta(hours=(start_time.hour - user_now_time.hour))
    elif start_time <= user_now_time <= end_time:
        time_to_send = timedelta()
    else:
        time_to_send = timedelta(hours=(24 - user_now_time.hour + start_time.hour))

    return user_now_datetime + time_to_send
