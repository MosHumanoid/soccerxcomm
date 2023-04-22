from typing import Callable

from .message import Message


class HttpServer:
    """The network server to communicate with clients."""

    def __init__(self, listen_port: int):
        """Initialize the server.

        Args:
            listen_port: The port to listen on.
        """

        self._listen_port: int = listen_port
        self._subscription_list: list[Callable[[Message], Message]] = []

    def start(self) -> None:
        """Start the server."""

        raise NotImplementedError
    
    def stop(self) -> None:
        """Stop the server."""

        raise NotImplementedError

    def subscribe(self, callback: Callable[[Message], Message]) -> None:
        """Subscribe to the server.

        Args:
            callback: The callback to call when a message is received.
        """

        self._subscription_list.append(callback)
