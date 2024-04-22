from fastapi import APIRouter

from api.v1.payments import router as payments_router
from core.config import settings

API_PREFIX_V1 = settings.url_prefix + "/api/v1"

all_v1_routers = APIRouter(prefix=API_PREFIX_V1)

all_v1_routers.include_router(payments_router, prefix="/payments", tags=["Payments"])
