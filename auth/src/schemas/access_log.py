import datetime as dt
import uuid

from pydantic import BaseModel


class AccessLogScheme(BaseModel):
    user_id: uuid.UUID
    ip_address: str
    user_agent: str
    origin: str
    created: dt.datetime
