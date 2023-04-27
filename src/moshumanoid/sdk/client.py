import asyncio

from .http_client import HttpClient
from .message import Message
from .logger import Logger


class Client:
    """The client to send commands to the server."""

    _logger = Logger("Client")

    def __init__(self, server_addr: str, token: str):
        """Initializes the client.

        Args:
            server_addr: The address of the server.
            token: The token of the game.
        """

        self._network_client = HttpClient(server_addr, token)
        self._token = token

        self._task_list = [
            asyncio.create_task(self._get_info_loop())
        ]

    async def _get_info_loop(self):
        await self._network_client.connect()

        while True:
            try:
                await asyncio.sleep(1)

                await self._network_client.send(Message(
                    {
                        "type": "get_game_info",
                        "bound_to": "server"
                    }
                ))

                await self._network_client.send(Message(
                    {
                        "type": "get_team_info",
                        "bound_to": "server"
                    }
                ))

            except Exception as e:
                self._logger.error(f'Failed to get info: {e}')
