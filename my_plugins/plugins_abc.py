from abc import ABC, abstractmethod

from discord.ui import Modal


class Plugin(ABC):
    def __init__(self, arguments=None):
        self.arguments = arguments

    @abstractmethod
    async def get_messages(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    async def modal(self) -> Modal:
        raise NotImplementedError
