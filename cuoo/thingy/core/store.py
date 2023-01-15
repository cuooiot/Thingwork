import asyncio
import sys
from typing import TYPE_CHECKING, List, Optional

import aiohttp

if TYPE_CHECKING:
    from .engine import Engine
    from ..component import Component
    from ..component.device import Device


class Store:
    def __init__(self, engine: 'Engine'):
        self.engine = engine

        # TODO: Confirm efficiency of keeping track of access in a list
        self.accessed_keys: List[str] = []
        self.accessed_objs: List['Component'] = []

    def reset(self, include_modified=True):
        self.current_accessor: Optional['Component'] = None
        self.current_device: Optional['Device'] = None

        if include_modified:
            self.modified_keys: List[str] = []

        self.is_dirty = False
        self.is_resolved = False

    async def ignite(self):
        async def _():
            while True:
                if self.engine.broker.is_ready:
                    return
                else:
                    await asyncio.sleep(1)

        try:
            await asyncio.wait_for(_(), timeout=5)  # TODO: Make a constant / configurable
            self.reset()

            for device in self.engine.broker.registered_devices:
                device.tick()

                for actuator in device.registered_actuators:
                    actuator.tick()

                for sensor in device.registered_sensors:
                    sensor.tick()
        except asyncio.TimeoutError:
            print('Devices never became ready') # TODO: Create an actual exception rather
            sys.exit()

        while True:
            try:
                await self.tick()
                await asyncio.sleep(0)
            except Exception as e:
                self.reset()
                import traceback # TODO: Nake this optional in production
                traceback.print_exception(e, file=sys.stderr)
                raise e

    async def tick(self):
        if self.is_dirty:
            await self.tick_dirty()
        elif self.is_resolved:
            await self.tick_resolved()

    async def tick_dirty(self):
        # If this loop resolved, we need to move onto the next step, so this is our marker
        self.is_resolved = True

        stack: List['Component'] = []
        for index, key in enumerate(self.accessed_keys):
            if key in self.modified_keys:
                accessor = self.accessed_objs[index]
                if accessor not in stack:
                    stack.append(accessor)

        self.reset()

        # Now we have a list of dependencies that we need to reload, Do it
        for accessor in stack:
            # First remove the existing accesses that a device / component may have made
            indexes = []
            for index, obj in enumerate(self.accessed_objs):
                if obj == accessor:
                    indexes.append(index)

            # Do the removing
            indexes.sort(reverse=True)
            for index in indexes:
                self.accessed_keys.pop(index)
                self.accessed_objs.pop(index)

            # Now re-fire it for its side effects
            accessor.tick()

    async def tick_resolved(self, client=None):
        # TODO: Split into a separate module?
        to_emit = self.engine.redis.pipeline()
        if client is not None:
            to_emit.json().get('registered_clients', f"$[?(@.id == '{client}')]")
        else:
            for path in set(self.modified_keys):
                device, path = path.split(':', 1)
                device = device.replace('"', '\"')
                path = path.replace('"', '\"')
                to_emit.json().get('registered_clients', f"$[?(@.device_id == '{device}' && @.path == '{path}')]")
        to_emit = to_emit.execute()

        data_keys = []
        data_pipeline = self.engine.redis.pipeline()
        for results in to_emit:
            for hook in results:
                token = f"{hook['device_id']}:{hook['path']}"
                if token not in data_keys:
                    data_keys.append(token)
                    data_pipeline.json().get(f"store:{hook['device_id']}", hook['path'])
        data_to_emit = data_pipeline.execute()

        pipelines = self.engine.redis.pipeline()
        for results in to_emit:
            for hook in results:
                token = f"{hook['device_id']}:{hook['path']}"
                data = data_to_emit[data_keys.index(token)]
                if data is not None:
                    data = data[0]

                session = aiohttp.ClientSession()
                remove = True
                try:
                    async with session.post(hook['client_url'], json={
                        'id': hook['id'],
                        'data': data
                    }) as response:
                        if response.status >= 200 and response.status < 300:
                            remove = False
                except Exception as e:
                    print(e, file=sys.stderr)

                await session.close()
                if remove:
                    pipelines.json().delete('registered_clients', f"$[?(@.id == '{hook['id']}')]")
        pipelines.execute()

        self.reset()
        if client is not None:
            return remove

    def access(self, device: 'Device', accessor: 'Component'):
        self.current_device = device
        self.current_accessor = accessor
        return self

    @property
    def namespace(self):
        return '' if self.current_device is None else f'{self.current_device.__class__.__name__}@{self.current_device.id()}'

    @property
    def fq_namespace(self):
        return 'store:' + self.namespace

    def __getitem__(self, key):
        # Reactivity helper
        if self.current_accessor != None:
            parts = []
            for fragment in key.split('.'):
                parts.append(fragment)
                self.accessed_keys.append(f'{self.namespace}:$.{".".join(parts)}')
                self.accessed_objs.append(self.current_accessor)

        # Data accessor
        # TODO: Add cache
        result = self.engine.r_json.get(self.fq_namespace, f'$.{key}')

        if result and result[0]:
            return result[0]

    def __setitem__(self, key, value):
        pipeline = self.engine.redis.pipeline()
        parts = []
        store_key = '$.' + key
        for fragment in store_key.split('.'):
            parts.append(fragment)
            path = '.'.join(parts)
            if path == store_key:
                pipeline.json().get(self.fq_namespace, path)
                pipeline.json().set(self.fq_namespace, path, value)
            else:
                pipeline.json().set(self.fq_namespace, path, {}, True)
        results = pipeline.execute()
        was = results[-2]

        was = was[0] if len(was) > 0 else None

        if (was != value):
            self.is_dirty = True

            # TODO: Maybe a set action should not count as an access?
            # parts = []
            # for fragment in key.split('.'):
            #     parts.append(fragment)
            #     path = ".".join(parts)
            #     self.accessed_keys.append(f'{self.namespace}:{path}')
            #     self.accessed_objs.append(self.current_accessor)

            parts = []
            for fragment in ('$.' + key).split('.'):
                parts.append(fragment)
                path = ".".join(parts)
                self.modified_keys.append(f'{self.namespace}:{path}')
