from typing import Optional
import os
import logging

from aiohttp import web

from atomic_counter import counter
from atomic_counter.persistence.file import FilePersistenceBackend


logger = logging.getLogger(__name__)


async def get_app(datadir: Optional[str]) -> web.Application:
    counter_repository = counter.CounterRespoitory()

    async def get_default_counter(namespace: str) -> counter.AtomicCounter:
        persistence_backend = None
        initial = 0

        if datadir is not None:
            persistence_backend = FilePersistenceBackend(path=os.path.join(datadir, namespace))
            initial = await persistence_backend.get_value() or 0

        return counter.AtomicCounter(
            initial=initial,
            max_value=100,
            persistence_backend=persistence_backend,
            persistence_factor=1,
        )

    if datadir is not None:
        os.makedirs(datadir, exist_ok=True)
        for statefile in os.listdir(datadir):
            logger.info(f"Loaded counter: {statefile}")
            counter_repository.counters[statefile] = await get_default_counter(statefile)

    class CounterView(web.View):
        async def get_counter(self) -> counter.AtomicCounter:
            namespace = self.request.match_info['namespace']
            return await counter_repository.get_counter(namespace=namespace, default_getter=get_default_counter)

        async def head(self):
            counter = await self.get_counter()
            return web.Response(text=str(counter.value))

        async def get(self):
            counter = await self.get_counter()
            val = await counter.increment()
            return web.Response(text=str(val))

    class Index(web.View):
        async def get(self):
            return web.json_response(data=list(counter_repository.counters.keys()))

    app = web.Application()
    app.add_routes([web.get('/', Index)])
    app.add_routes([web.get('/{namespace}', CounterView)])

    return app
