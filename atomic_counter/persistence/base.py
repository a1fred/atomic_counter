from typing import Optional


class PersistenceBackend():
    async def get_value(self) -> Optional[int]:
        raise NotImplementedError

    async def set_value(self, value: int) -> None:
        raise NotImplementedError
