from typing import TYPE_CHECKING, Type, List

from ..core.service import Service

if TYPE_CHECKING:
    from ..core.engine import Engine
    from ..web.controllers import Controller

    from aiohttp.web_routedef import RouteDef


class Web(Service):
    from .controllers.devices import Devices
    from .controllers.clients import Clients

    controllers: List[Type['Controller']] = [
        Devices,
        Clients,
    ]

    def __init__(self, engine: 'Engine'):
        self.engine = engine
        self.__routes: List['RouteDef'] = []

        for controller in self.__class__.controllers:
            controller(self)

        self.engine.app.add_routes(self.__routes)

    def add_route(self, route: 'RouteDef'):
        self.__routes.append(route)
