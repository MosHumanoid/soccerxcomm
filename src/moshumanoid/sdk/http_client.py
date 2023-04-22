import requests

from .message import Message


class HttpClient:
    """The network client to communicate with the server."""

    def __init__(self, server_addr: str):
        """Initialize the client.

        Args:
            server_addr: The address of the server.
        """

        self._server_address = server_addr

    def request(self, msg: Message) -> Message:
        """Send a message to the server and return the response.

        Args:
            msg: The message to send.
        """

        resp = requests.post(self._server_address, json=msg.get_json())

        return Message(resp.json())
