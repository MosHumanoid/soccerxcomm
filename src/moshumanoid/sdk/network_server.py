from abc import ABC, abstractmethod
from typing import Callable

from .message import Message


class INetworkServer(ABC):
    """The interface of the network server to communicate with clients."""

    @abstractmethod
    def broadcast(self, msg: Message) -> None:
        """Broadcasts a message to all clients.

        Args:
            msg: The message to broadcast.
        """

        raise NotImplementedError

    @abstractmethod
    def receive(self) -> Message:
        """Receives a message from all clients.

        Returns:
            The received message.
        """

        raise NotImplementedError

    @abstractmethod
    def send(self, msg: Message, token: str) -> None:
        """Sends a message to a client.

        Args:
            msg: The message to send.
            token: The token of the client to send the message to.
        """

        raise NotImplementedError

