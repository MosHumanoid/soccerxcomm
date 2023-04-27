import asyncio
from typing import Callable, List

from .message import Message
from .network_client import INetworkClient
from .logger import Logger

import httpx


class HttpClient(INetworkClient):
    """The HTTP client to communicate with the server."""

    _logger = Logger("HttpClient")

    def __init__(self, url: str, token: str):
        """Initializes a new instance of the HttpClient class.

        Args:
            url: The URL of the server.
            token: The token of the client.
        """
        self._url: str = url
        self._token: str = token

        self._callback_list: List[Callable[[Message], None]] = []
        self._task_list: List[asyncio.Task] = [
            asyncio.create_task(self._receive_loop()),
        ]

    async def register_callback(self, callback: Callable[[Message], None]) -> None:
        self._callback_list.append(callback)

    async def send(self, msg: Message, token: str) -> None:
        async with httpx.AsyncClient() as client:
            try:
                await client.post(
                    self._url,
                    headers={"Authorization": f"Bearer {self._token}"},
                    json=msg.to_dict(),
                )
            except Exception as e:
                self._logger.error(f"Error while sending: {e}")

    async def _receive_loop(self) -> None:
        async with httpx.AsyncClient() as client:
            while True:
                await asyncio.sleep(0.1)

                try:
                    response = await client.get(
                        self._url,
                        headers={"Authorization": f"Bearer {self._token}"},
                    )

                    if response.status_code == 404:
                        # 404 means no message.
                        continue

                    for callback in self._callback_list:
                        callback(Message(response.json()))

                except Exception as e:
                    self._logger.error(f"Error while receiving: {e}")
