import asyncio
from typing import TYPE_CHECKING, List

from ..core.service import Service

if TYPE_CHECKING:
    from ..core.engine import Engine
    from ..events.event import Event


class Events(Service):
    events: List['Event']

    def __init__(self, engine: 'Engine'):
        self.engine = engine

    def ignite(self):
        async def _():
            while True:
                self.process_removals()
                self.process_new()
                await asyncio.sleep(1)
                self.process_tick()

    def new(self, callback, time):
        event = Event(callback, time)
        self.events.append(event)
        return event

    def process_removals(self):
        for index, event in enumerate(self.events):
            if event.is_cancelled or event.is_resolved:
                self.events.pop(index)

    def process_new(self):
        for event in self.events:
            if (not event.is_registered):
                event.register()

    def process_tick(self):
        for event in self.events:
            if (not event.is_registered):
                event.register()
