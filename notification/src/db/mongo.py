import motor.motor_asyncio
from motor.core import AgnosticClient

mongo: AgnosticClient | None = None


def connect(dsn):
    global mongo
    if mongo:
        mongo.close()

    mongo = motor.motor_asyncio.AsyncIOMotorClient(dsn)

    return mongo


async def get_mongo() -> AgnosticClient:
    return mongo
