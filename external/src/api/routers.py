from fastapi import APIRouter

from api.v1.films import router as films_router
from api.v1.genres import router as genres_router
from api.v1.persons import router as persons_router
from core.config import settings

all_v1_routers = APIRouter()

API_PREFIX_V1 = settings.url_prefix + "/api/v1"

all_v1_routers.include_router(films_router, prefix=f"{API_PREFIX_V1}/films", tags=["Films"])
all_v1_routers.include_router(genres_router, prefix=f"{API_PREFIX_V1}/genres", tags=["Genres"])
all_v1_routers.include_router(persons_router, prefix=f"{API_PREFIX_V1}/persons", tags=["Persons"])
