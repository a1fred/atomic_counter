import asyncio
from typing import Optional

import aiofiles

from atomic_counter.persistence.base import PersistenceBackend


class FilePersistenceBackend(PersistenceBackend):
    def __init__(self, path: str):
        self._lock = asyncio.Lock()
        self.path = path

    async def get_value(self) -> Optional[int]:
        try:
            async with aiofiles.open(self.path, mode='r') as f:
                contents = await f.read()
                return int(contents.strip())
        except FileNotFoundError:
            return None

    async def set_value(self, value: int) -> None:
        async with aiofiles.open(self.path, mode='w') as f:
            await f.write(str(value))
