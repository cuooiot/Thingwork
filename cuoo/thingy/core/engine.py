# This is our service container...
import asyncio
import os

import aiohttp.web as aiohttp_web
from typing import TYPE_CHECKING, Type, List

from .container import Container
from .service import Service
from .store import Store
from cuoo.thingy.events import Events

if TYPE_CHECKING:
    from aiohttp.web import _Middleware
    from .context import Context


class Engine(Container):
    registered_contexts: List['Context'] = []
    middleware: List['_Middleware'] = []

    def __init__(self):
        super().__init__()
        self.attach(Store)
        self.attach(Events)

    def attach(self, service: Type['Service']):
        service = service(self)
        self.services[service.__class__.__name__.lower()] = service

    def register_context(self, context: 'Context'):
        self.registered_contexts.append(context)

    def ignite(self):
        self.ignite_events()
        self.ignite_devices()
        self.ignite_reactor()
        self.ignite_web()

    def ignite_events(self):
        async def _(_):
            task = asyncio.create_task(self.events.ignite())
            yield
            task.cancel()
            await task

        self.app.cleanup_ctx.append(_)

    def ignite_devices(self):
        async def _(_):
            ignite = asyncio.create_task(self.broker.ignite())
            yield
            self.broker.extinguish()
            ignite.cancel()
            await ignite

        self.app.cleanup_ctx.append(_)

    def ignite_reactor(self):
        async def _(_):
            task = asyncio.create_task(self.store.ignite())
            yield
            task.cancel()
            self.redis.save()
            await task

        self.app.cleanup_ctx.append(_)

    def ignite_web(self):
        props = {
            'port': 2866
        }
        props['port'] = os.environ.get('HOST_PORT') or 2866

        if int(os.environ.get('SSL_ENABLED')) != 0:
            import ssl
            props['ssl_context'] = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            props['ssl_context'].load_cert_chain(
                certfile=os.environ.get('SSL_CERT', '/run/secrets/ssl/cert'),
                keyfile=os.environ.get('SSL_KEY', '/run/secrets/ssl/key'),
            )

        aiohttp_web.run_app(self.app, **props)
