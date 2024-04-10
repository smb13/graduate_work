from fastapi import APIRouter

from api.v1.bookmarks import router as bookmarks_router
from api.v1.ratings import router as ratings_router
from api.v1.reviews import router as reviews_router
from core.config import settings

all_v1_routers = APIRouter()

API_PREFIX_V1 = settings.url_prefix + "/api/v1"

all_v1_routers.include_router(ratings_router, prefix=f"{API_PREFIX_V1}/ratings", tags=["Ratings API"])
all_v1_routers.include_router(reviews_router, prefix=f"{API_PREFIX_V1}/reviews", tags=["Reviews API"])
all_v1_routers.include_router(bookmarks_router, prefix=f"{API_PREFIX_V1}/bookmarks", tags=["Bookmarks API"])
