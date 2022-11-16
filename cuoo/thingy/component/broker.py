import asyncio
import functools
from typing import TYPE_CHECKING, List, Type

from ..core.context import Context

if TYPE_CHECKING:
    from .device import Device
    from ..core.engine import Engine


class Broker:
    devices: List[Type['Device']]

    def __init__(self, engine: 'Engine'):
        self.engine = engine
        self.__limit = 0
        self.__ready = 0

        def _(device: Type['Device']) -> 'Device':
            return Context(engine, self, device).element

        self.registered_devices: List['Device'] = list(map(_, self.__class__.devices or []))

    def ready(self):
        self.__ready += 1

    @property
    def is_ready(self):
        return self.__ready >= self.__limit

    async def ignite(self):
        def _(acc: List, device: 'Device'):
            tasks = device.ignite()
            self.__limit += len(tasks)
            return acc + tasks

        return await asyncio.gather(
            *functools.reduce(_, self.registered_devices, [])
        )

    def extinguish(self):
        print('ext')
        map(lambda device: device.extinguish(), self.registered_devices)
