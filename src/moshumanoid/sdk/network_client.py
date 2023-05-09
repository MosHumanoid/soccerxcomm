from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine

from .message import Message


class INetworkClient(ABC):
    """Abstract interface for a network client."""

    @abstractmethod
    async def connect(self) -> None:
        """Connects to the server."""

        raise NotImplementedError

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnects from the server."""

        raise NotImplementedError

    @abstractmethod
    async def register_callback(self, callback: Callable[[Message], Coroutine[Any, Any, None]]) -> None:
        """Registers a callback function to be called when a message is received.

        Args:
            callback: The callback function to register.
        """

        raise NotImplementedError

    @abstractmethod
    async def send(self, msg: Message) -> None:
        """Sends a message to the server.

        Args:
            msg: The message to send.
        """

        raise NotImplementedError
