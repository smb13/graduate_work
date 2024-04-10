import json
from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from redis import Redis


class StateStorage(metaclass=ABCMeta):
    @abstractmethod
    def save_state(self, state: dict[str, Any]) -> None:
        pass

    @abstractmethod
    def retrieve_state(self) -> dict[str, Any]:
        pass


class JsonStorage(StateStorage):
    def __init__(self, file_path: str, *args, **kwargs) -> None:
        self.file_path = file_path
        super().__init__(*args, **kwargs)

    def save_state(self, state: dict[str, Any]) -> None:
        try:
            with open(self.file_path, "r+") as file:
                file_content: dict[str, Any] = json.load(file)
                file.seek(0)
                json.dump(file_content | state, file)
                file.truncate()
        except (FileNotFoundError, json.JSONDecodeError):
            with open(self.file_path, "w") as file:
                json.dump(state, file)
                file.truncate()

    def retrieve_state(self) -> dict[str, Any]:
        try:
            with open(self.file_path) as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}


class RedisStorage(StateStorage):
    def __init__(self, redis: "Redis", *args, **kwargs) -> None:
        self.redis = redis
        super().__init__(*args, **kwargs)

    data_key = "state_data"

    def save_state(self, state: dict[str, Any]) -> None:
        json_data = self.redis.get(self.data_key) or "{}"  # noqa: P103
        data = json.loads(json_data)
        updated_data = data | state
        self.redis.set(self.data_key, json.dumps(updated_data))

    def retrieve_state(self) -> dict[str, Any]:
        return json.loads(self.redis.get(self.data_key) or "{}")  # noqa: P103


class State:
    def __init__(self, storage: StateStorage) -> None:
        self.storage = storage
        self.storage.retrieve_state()

    def set_state(self, key: str, value: Any) -> None:
        self.storage.save_state({key: value})

    def get_state(self, key: str) -> Any | None:
        state_dict = self.storage.retrieve_state()
        return state_dict.get(key)
