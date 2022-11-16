import uuid
from typing import TYPE_CHECKING

from aiohttp.web import Request, json_response, post, HTTPFailedDependency

from . import Controller

if TYPE_CHECKING:
    from .. import Web


class Clients(Controller):
    def __init__(self, web: 'Web'):
        super().__init__(web)
        web.add_route(post('/subscribe', self.subscribe))

    async def subscribe(self, request: Request):
        data = await request.post()
        id = str(uuid.uuid4())
        pipeline = self.web.engine.redis.pipeline()
        pipeline.json().set('registered_clients', '$', [], True)
        pipeline.json().arrappend('registered_clients', '$', {
            'id': id,
            'device_id': data['device_id'],
            'client_url': data['client_url'],
            'path': data['path']
        })
        pipeline.execute()

        # failed = await self.web.engine.store.tick_resolved(client=id)

        # if failed:
        if False:
            raise HTTPFailedDependency()
        else:
            return json_response({
                'id': id
            })
