import argparse
import asyncio

from db import alchemy
from main import lifespan
from schemas.user import UserCreate
from services.roles import RolesService, get_roles_service
from services.users import UsersService, get_users_service


@lifespan(None)
async def create_roles_and_admin(username: str, password: str) -> None:
    async with alchemy.async_session() as session:
        users_service: UsersService = get_users_service(alchemy=session)
        roles_service: RolesService = get_roles_service(alchemy=session)

        users_role = await roles_service.get_or_create_user_role()
        admin_role = await roles_service.get_or_create_admin_role()

        user_create = UserCreate(
            login=username,
            password=password,
            first_name="Admin",
            last_name="User",
        )
        user = await users_service.retrieve(username=user_create.login)
        if not user:
            user = await users_service.create(user_create)

        await roles_service.add_roles_to_user(
            user=user,
            role_ids=(users_role.id, admin_role.id),
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create admin user")
    parser.add_argument(
        "--username",
        type=str,
        default="admin",
        help="Username for admin user",
    )
    parser.add_argument(
        "--password",
        type=str,
        default="password",
        help="Password for admin user",
    )
    args = parser.parse_args()
    username = args.username
    password = args.password

    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_roles_and_admin(username, password))
    loop.close()
