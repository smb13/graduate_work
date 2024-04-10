from uuid import UUID

from pydantic import BaseModel, Field


class WebSocketNotification(BaseModel):
    request_id: str
    notice_id: UUID
    message_id: UUID
    user_id: UUID
    message_meta: dict = Field(default_factory=dict)
    message_body: str
