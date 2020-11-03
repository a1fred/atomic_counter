from typing import Optional
import asyncio
import argparse
from aiohttp import web
import logging

from atomic_counter import server


logger = logging.getLogger(__name__)


async def get_app(datadir: Optional[str]):
    return await server.get_app(datadir=datadir)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default="127.0.0.1")
    parser.add_argument('--port', default="8888")
    parser.add_argument('--datadir', default=None)
    logging.basicConfig(level=logging.DEBUG)

    args = vars(parser.parse_args())

    app = await get_app(datadir=args['datadir'])

    logger.info(f"Serving on: http://{args['host']}:{args['port']}")

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host=args['host'], port=args['port'])
    await site.start()

    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        return await runner.cleanup()


asyncio.run(main())
