from http import HTTPStatus

from fastapi import HTTPException
from src.core.logger import logger
from src.db.sendgrid.accessor import SendgridAccessor

sendgrid_instance: SendgridAccessor = SendgridAccessor()


def get_sendgrid() -> SendgridAccessor:
    if sendgrid_instance.connect is None:
        logger.critical("Sendgrid is not setup!")
        raise HTTPException(status_code=HTTPStatus.SERVICE_UNAVAILABLE)
    return sendgrid_instance
