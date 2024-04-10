from fastapi import APIRouter

from api.v1.notifications import router as notifications_router
from api.v1.tasks import router as tasks_router
from core.config import settings

all_v1_routers = APIRouter()

API_PREFIX_V1 = settings.url_prefix + "/api/v1"

all_v1_routers.include_router(notifications_router, prefix=f"{API_PREFIX_V1}/notifications", tags=["Notifications API"])
all_v1_routers.include_router(tasks_router, prefix=f"{API_PREFIX_V1}/tasks", tags=["Tasks API"])
