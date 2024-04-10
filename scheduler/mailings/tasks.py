import logging
import uuid
from urllib.parse import urljoin

from django.conf import settings

import requests
from config.celery import app

logger = logging.getLogger(__name__)


@app.task(name="task_send_mailings")
def task_send_mailings(template_id: uuid.UUID, **kwargs) -> None:
    path: str = f'/api/v1/{kwargs.get("users_selector", {}).get("url_method")}'

    requests.post(
        urljoin(settings.EPK_API_URL, path),
        json={
            "template_id": template_id,
            "subject": kwargs.get("name"),
            "type": "email",
            "user_id": kwargs.get("users_selector", {}).get("user_id"),
        },
    )
