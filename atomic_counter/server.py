import logging
import random

from aiohttp import web
from atomic_counter import counter


logger = logging.getLogger(__name__)


async def get_app(datadir: str) -> web.Application:
    persistence_rate = 1
    counter_repository = counter.CounterRespoitory(datadir=datadir)
    await counter_repository.load()

    class CounterView(web.View):
        async def get_counter(self) -> counter.AtomicCounter:
            namespace = self.request.match_info['namespace']
            return await counter_repository.get_counter(namespace=namespace)

        async def head(self):
            counter = await self.get_counter()
            return web.Response(text=str(counter.value))

        async def get(self):
            counter = await self.get_counter()
            val = await counter.increment()

            if random.randrange(persistence_rate) == 0:
                await counter_repository.save(self.request.match_info['namespace'])

            return web.Response(text=str(val))

    class Index(web.View):
        async def get(self):
            data = {}

            for ns, cnt in counter_repository.counters.items():
                data[ns] = {
                    'value': cnt.value,
                    'max_value': cnt.max_value,
                }
            return web.json_response(data=data)

    app = web.Application()
    app.add_routes([web.get('/', Index)])
    app.add_routes([web.get('/{namespace}', CounterView)])

    return app
