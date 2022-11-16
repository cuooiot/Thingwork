# This is our service container...
import asyncio
import os

import aiohttp.web as aiohttp_web
from typing import TYPE_CHECKING, Type, List, Union

from .services import Services

if TYPE_CHECKING:
    from aiohttp.web import _Middleware
    from ..component.broker import Broker
    from ..web import Web
    from .context import Context


class Engine(Services):
    registered_contexts: List['Context'] = []
    middleware: List['_Middleware'] = []

    def attach(self, service: Type[Union['Broker', 'Web']]):
        from ..component.broker import Broker
        from ..web import Web

        service = service(self)
        if isinstance(service, Broker):
            self.__broker = service
        elif isinstance(service, Web):
            self.__web = service

    @property
    def broker(self):
        return self.__broker

    @property
    def web(self):
        return self.__web

    def register_context(self, context: 'Context'):
        self.registered_contexts.append(context)

    def ignite(self):
        self.ignite_devices()
        self.ignite_reactor()
        self.ignite_web()

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
        if os.environ.get('HOST_PORT', False):
            props['port'] = os.environ.get('HOST_PORT', 2866)

        if int(os.environ.get('SSL_ENABLED', False)) != 0:
            import ssl
            props['ssl_context'] = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            props['ssl_context'].load_cert_chain(
                certfile=os.environ.get('SSL_CERT', '/run/secrets/ssl/cert'),
                keyfile=os.environ.get('SSL_KEY', '/run/secrets/ssl/key'),
            )

        aiohttp_web.run_app(self.app, **props)
