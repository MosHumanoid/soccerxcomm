from abc import ABC, abstractmethod
from typing import Callable

from .message import Message


class INetworkClient(ABC):
    """The interface of the network client to communicate with the server."""

    @abstractmethod
    def receive(self) -> Message:
        """Receives a message from the server.

        Returns:
            The received message.
        """

        raise NotImplementedError

    @abstractmethod
    def send(self, msg: Message) -> None:
        """Sends a message to the server.

        Args:
            msg: The message to send.
        """

        raise NotImplementedError
