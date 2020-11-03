from typing import Optional
import sys
import asyncio
import random

from atomic_counter.persistence.base import PersistenceBackend


MAX_VALUE = sys.maxsize
INCREMENT_BY = 1


class AtomicCounter:
    def __init__(
        self,
        initial: int = 0,
        max_value: int = MAX_VALUE, increment_by: int = INCREMENT_BY,
        persistence_backend: Optional[PersistenceBackend] = None,
        persistence_factor: int = 1,
    ):
        self.persistence_backend = persistence_backend
        self.persistence_factor = persistence_factor

        self.value = initial

        self.max_value = max_value
        self.increment_by = increment_by

        self._lock = asyncio.Lock()

    async def increment(self):
        async with self._lock:
            self.value += self.increment_by

            if self.value > self.max_value:
                self.value %= self.max_value

            if random.randrange(self.persistence_factor) == 0:
                await self.persistence_backend.set_value(self.value)

            return self.value


class CounterRespoitory:
    def __init__(self):
        self.counters = {}
        self._lock = asyncio.Lock()

    async def get_counter(self, namespace: str, default_getter) -> AtomicCounter:
        result = self.counters.setdefault(namespace, None)
        if result is not None:
            return result

        async with self._lock:
            new_counter = await default_getter(namespace)
            self.counters[namespace] = new_counter
            return new_counter
