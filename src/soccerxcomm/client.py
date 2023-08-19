from __future__ import annotations

import asyncio
import datetime
from typing import List

import numpy as np

from .game_info import GameInfo
from .game_stage_kind import GameStageKind
from .http_client import HttpClient
from .logger import Logger
from .message import Message
from .network_client import INetworkClient


class Client:
    """The client to send commands to the server."""

    _logger = Logger("Client")

    def __init__(self, host: str, port_controller: int, port_streaming: int, token: str):
        """Initializes the client.

        Args:
            host: The server address.
            port_controller: The port of the controller server.
            port_streaming: The port of the streaming server.
            token: The token of the game.
        """

        self._is_callback_registered: bool = False
        self._controller_network_client: INetworkClient = HttpClient(
            host, port_controller, token)
        self._streaming_network_client: INetworkClient = HttpClient(
            host, port_streaming, token)
        self._task_list: List[asyncio.Task] = []

        # Game information
        self._game_info: GameInfo | None = None

        # Captured image
        self._captured_image: np.ndarray | None = None

    async def connect(self) -> None:
        """Connects to the server."""

        if not self._is_callback_registered:
            await self._controller_network_client.register_callback(self._controller_callback)
            await self._streaming_network_client.register_callback(self._streaming_callback)
            self._is_callback_registered = True

        await self._controller_network_client.connect()
        await self._streaming_network_client.connect()

        self._task_list.append(asyncio.create_task(self._controller_loop()))

    async def disconnect(self) -> None:
        """Disconnects from the server."""

        for task in self._task_list:
            task.cancel()

        self._task_list.clear()

        await self._controller_network_client.disconnect()
        await self._streaming_network_client.disconnect()

    async def get_game_info(self) -> GameInfo | None:
        """Gets the game information.

        Returns:
            The game information.
        """

        return self._game_info
    
    async def get_captured_image(self) -> np.ndarray | None:
        """Gets the captured image.

        Returns:
            The captured image.
        """

        return self._captured_image

    async def _controller_callback(self, msg: Message) -> None:
        try:
            message_bound_to: str = msg.get_bound_to()

            if message_bound_to == 'server':
                return

            message_type: str = msg.get_type()

            if message_type == 'get_game_info':
                self._game_info = GameInfo(
                    stage=GameStageKind(str(msg.to_dict()['stage'])),
                    start_time=datetime.datetime.fromtimestamp(
                        int(msg.to_dict()['start_time'])),
                    end_time=datetime.datetime.fromtimestamp(
                        int(msg.to_dict()['end_time'])),
                    score=msg.to_dict()['score'],
                    simulation_rate=float(msg.to_dict()['simulation_rate']),
                )

            elif message_type == 'push_robot_status':
                # TODO: Implement this
                pass

        except Exception as e:
            self._logger.error(f'Failed to handle message: {e}')

    async def _controller_loop(self) -> None:
        while True:
            try:
                await asyncio.sleep(1)

                await self._controller_network_client.send(Message(
                    {
                        "type": "get_game_info",
                        "bound_to": "server"
                    }
                ))

                await self._controller_network_client.send(Message(
                    {
                        "type": "get_team_info",
                        "bound_to": "server"
                    }
                ))

            except Exception as e:
                self._logger.error(f'Failed to get info: {e}')

    async def _streaming_callback(self, msg: Message) -> None:
        try:
            message_bound_to: str = msg.get_bound_to()

            if message_bound_to == 'server':
                return

            message_type: str = msg.get_type()

            if message_type == 'push_captured_image':
                data: bytes = msg.to_dict()['data']
                shape: List[int] = msg.to_dict()['shape']
                self._captured_image = np.frombuffer(
                    data, dtype=np.uint8).reshape(shape)

        except Exception as e:
            self._logger.error(f'Failed to handle message: {e}')
