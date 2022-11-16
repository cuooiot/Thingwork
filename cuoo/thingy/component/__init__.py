from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .broker import Broker
    from ..core.context import Context


class Component:
    def __init__(self, broker: 'Broker', context: 'Context'):
        """
        Set up your component wrapper, but do not yet start your devices
        :return:
        """
        self.broker: 'Broker' = broker
        self.context: 'Context' = context

    async def create(self):
        """
        Open up your device and place in global scope. Only called once and not reactive
        :return:
        """
        self.broker.ready()

    def tick(self):
        """
        Implement tick to provide complex linking/controlling logic for this device.
        Will be called after everything is opened
        :return:
        """
        pass

    def destroy(self):
        """
        Close up your device for shutdown. Only called once and not reactive
        :return:
        """
        pass
