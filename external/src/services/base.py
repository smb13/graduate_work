from core.types import DataOptType, RequestData
from services.cache import BaseCache
from services.database import BaseDatabase


class BaseService:
    def __init__(
        self,
        cache: BaseCache,
        database: BaseDatabase,
    ) -> None:
        self.cache = cache
        self.database = database

    async def get_data(self, request_data: RequestData) -> DataOptType:
        # Пытаемся получить данные из кеша
        data = await self.cache.get(request_data)
        if not data:
            # Если данных нет в кеше, то ищем его в базе данных
            data = await self.database.get(request_data)
            if not data:
                # Если данные отсутствуют в базе данных, значит, их вообще нет
                return None
            # Сохраняем данные в кеш
            await self.cache.put(data, request_data)

        return data
