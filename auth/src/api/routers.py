from fastapi import APIRouter

from api.v1.account import router as account_router
from api.v1.auth import router as auth_router
from api.v1.oauth import router as oauth_router
from api.v1.roles import router as roles_router
from api.v1.users import router as users_router
from core.config import settings

API_PREFIX_V1 = settings.url_prefix + "/api/v1"

all_v1_routers = APIRouter(prefix=API_PREFIX_V1)

all_v1_routers.include_router(account_router, prefix="/account", tags=["Account"])
all_v1_routers.include_router(auth_router, prefix="/auth", tags=["Auth"])
all_v1_routers.include_router(oauth_router, prefix="/oauth", tags=["OAuth"])
all_v1_routers.include_router(users_router, prefix="/users", tags=["Users"])
all_v1_routers.include_router(roles_router, prefix="/roles", tags=["Roles"])
