from typing import Dict
import sys
import asyncio
import os
import logging

from atomic_counter.persistence import FilePersistenceBackend

logger = logging.getLogger(__name__)


MAX_VALUE = sys.maxsize
INCREMENT_BY = 1


class AtomicCounter:
    def __init__(
        self,
        persistence_backend: FilePersistenceBackend,
        initial: int,
        max_value: int = MAX_VALUE, increment_by: int = INCREMENT_BY,
    ):
        self.persistence_backend = persistence_backend

        self.value = initial

        self.max_value = max_value
        self.increment_by = increment_by

        self._lock = asyncio.Lock()

    async def increment(self):
        async with self._lock:
            self.value += self.increment_by

            if self.value > self.max_value:
                self.value %= self.max_value

            return self.value


class CounterRespoitory:
    def __init__(self, datadir: str):
        self.counters: Dict[str, AtomicCounter] = {}
        self.datadir = datadir
        self._lock = asyncio.Lock()

    async def load(self):
        os.makedirs(self.datadir, exist_ok=True)
        for statefile in os.listdir(self.datadir):
            logger.info(f"Loaded counter: {statefile}")
            self.counters[statefile] = await self.get_default_counter(statefile)

    async def save(self, namespace: str):
        assert namespace in self.counters
        counter_inst = self.counters[namespace]
        data = {
            "initial": counter_inst.value,
            "max_value": counter_inst.max_value,
        }
        await counter_inst.persistence_backend.save(data)

    async def get_default_counter(self, namespace: str) -> AtomicCounter:
        persistence_backend = None
        data = {
            "initial": 0,
            "max_value": 100,
        }

        if self.datadir is not None:
            persistence_backend = FilePersistenceBackend(path=os.path.join(self.datadir, namespace))
            loaded_data = await persistence_backend.load()
            if loaded_data is not None:
                data = loaded_data

        return AtomicCounter(
            persistence_backend=persistence_backend,
            **data,
        )

    async def get_counter(self, namespace: str) -> AtomicCounter:
        result = self.counters.setdefault(namespace, None)  # type:ignore
        if result is not None:
            return result

        async with self._lock:
            new_counter = await self.get_default_counter(namespace)
            self.counters[namespace] = new_counter
            return new_counter
