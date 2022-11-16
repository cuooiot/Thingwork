import asyncio
from typing import TYPE_CHECKING, Union, List, Type

from . import Component
from .actuator import Actuator
from .sensor import Sensor

if TYPE_CHECKING:
    from .broker import Broker
    from ..core.context import Context


class Device(Component):
    actuators: List[Type['Actuator']] = []
    sensors: List[Type['Sensor']] = []

    def __init__(self, broker: 'Broker', context: 'Context'):
        super().__init__(broker, context)
        self.registered_actuators: List['Actuator']
        self.registered_sensors: List['Sensor']

    def ignite(self) -> List:
        def _(component: Type[Union['Actuator', 'Sensor']]) -> Union['Actuator', 'Sensor']:
            return self.context.extend(component).element

        self.registered_actuators: List['Actuator'] = list(map(_, self.__class__.actuators))
        self.registered_sensors: List['Sensor'] = list(map(_, self.__class__.sensors))

        def _(component: Union['Device', 'Actuator', 'Sensor']):
            return asyncio.create_task(component.create())

        return [_(self)] \
               + list(map(_, self.registered_actuators)) \
               + list(map(_, self.registered_sensors))

    def extinguish(self):
        def _(component: Union['Device', 'Actuator', 'Sensor']):
            component.destroy()

        map(_, self.registered_sensors)
        map(_, self.registered_actuators)
        _(self)

    def ref(self):
        return f'{self.__class__.__name__}@GENERIC'

    def id(self):
        return f'GENERIC'
