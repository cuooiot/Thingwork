import json
from typing import TYPE_CHECKING

from aiohttp.web import Response, get

from . import Controller

if TYPE_CHECKING:
    from .. import Web


class Devices(Controller):
    def __init__(self, web: 'Web'):
        super().__init__(web)
        web.add_route(get('/devices', self.index))

    async def index(self, _):
        devices = []
        for device in self.web.engine.broker.registered_devices:
            devices.append({
                'id': device.ref(),
                'type': device.__class__.__name__
            })
        return Response(text=json.dumps(devices))
