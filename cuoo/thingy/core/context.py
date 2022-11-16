'''
This is a proxy class which provides access to the Bus to a downstream device / sensor / actuator
'''
from copy import copy
from typing import TYPE_CHECKING, Type, Union

from .store import Store

if TYPE_CHECKING:
    from ..component.actuator import Actuator
    from ..component.sensor import Sensor
    from ..component.device import Device
    from ..component.broker import Broker
    from ..component import Component
    from .engine import Engine


class Context:
    def __init__(self, engine: 'Engine', broker: 'Broker', device: Type['Device']):
        self.__engine = engine
        self.__broker = broker
        self.__component = None

        self.__engine.register_context(self)  # Self register
        self.__device = device(broker, self)  # Create device

    def extend(self, child: Type[Union['Sensor', 'Actuator']]) -> 'Context':
        _ = copy(self)
        _.__component = child(self.__broker, _)
        return _

    @property
    def store(self) -> Store:
        return self.__engine.store.access(self.__device, self.element)

    @property
    def device(self) -> 'Device':
        return self.__device

    @property
    def element(self) -> 'Component':
        return self.__component or self.__device
