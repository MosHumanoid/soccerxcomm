from .message import Message


class Client:
    """The client to send commands to the server."""

    def __init__(self, server_addr: str, token: str):
        """Initializes the client.

        Args:
            server_addr: The address of the server.
            token: The token of the game.
        """

        # self._network_client = HttpClient(server_addr)
        self._token = token

    def start_streaming(self) -> None:
        """Starts image streaming."""

        message = Message({
            'type': 'start_streaming',
            'bound_to': 'server',
            'token': self._token
        })

        # self._network_client.send(message)

    def stop_streaming(self) -> None:
        """Stops image streaming."""

        message = Message({
            'type': 'stop_streaming',
            'bound_to': 'server',
            'token': self._token
        })

        # self._network_client.send(message)
