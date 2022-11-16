from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .. import Web


class Controller:
    def __init__(self, web: 'Web'):
        self.web = web
