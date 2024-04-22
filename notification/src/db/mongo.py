import motor.motor_asyncio
from motor.core import AgnosticClient

mongo: AgnosticClient | None = None


def connect(dsn: str) -> AgnosticClient:
    global mongo
    if mongo:
        mongo.close()

    return motor.motor_asyncio.AsyncIOMotorClient(dsn)


async def get_mongo() -> AgnosticClient:
    if not mongo:
        raise RuntimeError("Mongo is not initialized")

    return mongo
