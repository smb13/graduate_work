import motor.motor_asyncio
from motor.core import AgnosticClient

mongo: AgnosticClient | None = None


def connect(dsn: str) -> AgnosticClient:
    global mongo
    if mongo:
        mongo.close()

    mongo = motor.motor_asyncio.AsyncIOMotorClient(dsn)

    return mongo  # noqa: PIE781 R504


async def get_mongo() -> AgnosticClient:
    return mongo
