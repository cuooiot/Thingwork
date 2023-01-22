import abc

from cuoo.thingy.core.engine import Engine


class Service:
    @abc.abstractmethod
    def __init__(self, engine: 'Engine'):
        pass
