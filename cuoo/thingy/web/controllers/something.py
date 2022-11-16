from typing import TYPE_CHECKING

from aiohttp.web import Request, Response, get

from . import Controller

if TYPE_CHECKING:
    from .. import Web


class Something(Controller):
    def __init__(self, web: 'Web'):
        super().__init__(web)
        web.add_route(get('/', self.index))

    async def index(self, request: Request):
        self.web.engine.store.access(
            self.web.engine.broker.registered_devices[0],
            self.web.engine.broker.registered_devices[0]
        )
        text = f'Path: {request.query_string}\nVal: {self.web.engine.store["a"]}'
        return Response(text=text)
