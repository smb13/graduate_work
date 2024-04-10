import uuid
from uuid import UUID

from pydantic import Field

from schemas.notifications import EmailNotification, PushNotification


class EmailTask(EmailNotification):
    """Задача на отправку уведомления по электронной почте"""

    id: UUID = Field(default=..., description="Идентификатор уведомления", examples=[uuid.uuid4()])


class PushTask(PushNotification):
    """Задание на отправку push уведомления"""

    id: UUID = Field(default=..., description="Идентификатор уведомления", examples=[uuid.uuid4()])
