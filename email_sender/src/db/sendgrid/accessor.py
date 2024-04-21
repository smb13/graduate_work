from urllib.error import URLError

import sendgrid
from src.core.config import settings
from src.core.logger import logger
from src.db.abstract import AbstractAccessor


# https://github.com/sendgrid/sendgrid-python
class SendgridAccessor(AbstractAccessor):
    def __init__(self) -> None:
        self._client: sendgrid.SendGridAPIClient | None = None
        self.is_setup_client: bool = False

    def setup(self) -> sendgrid.SendGridAPIClient:
        """
        Инициализация клиента Sendgrid.
        """
        if not self.is_setup_client:
            try:
                self._client = sendgrid.SendGridAPIClient(api_key=settings.email.api_sendgrid)
                self.is_setup_client = True
            except URLError:
                self.is_setup_client = False
                logger.exception("Не удалось соединиться с Sendgrid - неверный API_KEY")
        return self._client

    @property
    def connect(self) -> sendgrid.SendGridAPIClient:
        return self.setup()
