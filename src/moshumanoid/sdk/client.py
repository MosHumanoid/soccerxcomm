from .http_client import HttpClient
from .message import Message


class Client:
    """The client to send commands to the server."""

    def __init__(self, server_addr: str, token: str):
        """Initialize the client.

        Args:
            server_addr: The address of the server.
            token: The token of the game.
        """

        self._http_client = HttpClient(server_addr)
        self._token = token

    def start_streaming(self) -> None:
        """Start image streaming."""

        message = Message({
            'type': 'start_streaming',
            'bound_to': 'server',
            'token': self._token
        })

        self._http_client.request(message)

    def stop_streaming(self) -> None:
        """Stop image streaming."""

        message = Message({
            'type': 'stop_streaming',
            'bound_to': 'server',
            'token': self._token
        })

        self._http_client.request(message)
