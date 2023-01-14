from typing import TYPE_CHECKING

import os

import redis
from aiohttp import web

from .store import Store

if TYPE_CHECKING:
    from redis.commands.json import JSON
    from aiohttp.web import Application


class Services:
    def __init__(self):
        from ..web.middleware.authentication import Authentiction
        middleware = \
            [
                Authentiction.handle
            ] + (self.middleware or []) + []
        # Storage stuff
        self.__app = web.Application(middlewares=middleware)
        self.__redis = redis.Redis(
            host=os.environ.get('REDIS_HOST', 'redis'),
            port=os.environ.get('REDIS_PORT', 6379),
            db=os.environ.get('REDIS_DB', 0),
        )
        self.__store = Store(self)

    # Services
    @property
    def app(self) -> 'Application':
        return self.__app

    @property
    def store(self) -> 'Store':
        return self.__store

    @property
    def redis(self) -> redis.Redis:
        return self.__redis

    @property
    def r_json(self) -> 'JSON':
        return self.__redis.json()
