from typing import TYPE_CHECKING

from . import Component

if TYPE_CHECKING:
    from ..component.broker import Broker
    from ..core.context import Context


class Actuator(Component):
    pass