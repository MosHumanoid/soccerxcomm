from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine

from .message import Message


class INetworkServer(ABC):
    """Abstract interface for a network server."""

    @abstractmethod
    async def broadcast(self, msg: Message) -> None:
        """Broadcasts a message to all clients.

        Args:
            msg: The message to broadcast.
        """

        raise NotImplementedError

    @abstractmethod
    async def register_callback(self, callback: Callable[[str, Message], Coroutine[Any, Any, None]]) -> None:
        """Registers a callback function to be called when a message is received.

        Args:
            callback: The callback function to register. The arguments are the token of the client and the message.
        """

        raise NotImplementedError

    @abstractmethod
    async def send(self, msg: Message, token: str) -> None:
        """Sends a message to a client.

        Args:
            msg: The message to send.
            token: The token of the client to send the message to.
        """

        raise NotImplementedError

    @abstractmethod
    async def start(self) -> None:
        """Starts the server."""

        raise NotImplementedError

    @abstractmethod
    async def stop(self) -> None:
        """Stops the server."""

        raise NotImplementedError
