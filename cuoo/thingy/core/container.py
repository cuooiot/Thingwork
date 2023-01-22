from typing import TYPE_CHECKING, Dict

import os

import redis
from aiohttp import web

from .store import Store

if TYPE_CHECKING:
    from redis.commands.json import JSON
    from aiohttp.web import Application
    from cuoo.thingy.events import Events


class Container:
    services: Dict[str, object] = {}

    def __init__(self):
        from ..web.middleware.authentication import Authentiction
        middleware = \
            [
                Authentiction.handle
            ] + (self.middleware or []) + []
        # Storage stuff
        self.services['app'] = web.Application(middlewares=middleware)
        self.services['redis'] = redis.Redis(
            host=os.environ.get('REDIS_HOST', 'redis'),
            port=os.environ.get('REDIS_PORT', 6379),
            db=os.environ.get('REDIS_DB', 0),
        )

    # Services
    @property
    def app(self) -> 'Application':
        return self.services['app']

    @property
    def store(self) -> 'Store':
        return self.services['store']

    @property
    def redis(self) -> redis.Redis:
        return self.services['redis']

    @property
    def r_json(self) -> 'JSON':
        return self.redis.json()

    @property
    def broker(self):
        return self.services['broker']

    @property
    def web(self):
        return self.services['web']

    @property
    def events(self) -> 'Events':
        return self.services['events']
