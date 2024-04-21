from fastapi import APIRouter
from src.api.v1.base import router as base_router
from src.core.config import settings

API_PREFIX_V1 = f"/api/{settings.app.version}"

all_v1_routers = APIRouter()
all_v1_routers.include_router(base_router, prefix=API_PREFIX_V1)
