from __future__ import annotations

from typing import Dict, List

import numpy as np

from .client_info import ClientInfo
from .game_info import GameInfo
from .http_server import HttpServer
from .logger import Logger
from .message import Message
from .network_server import INetworkServer


class Server:
    """The MosHumanoid server."""

    _logger = Logger("Server")

    def __init__(self, port_controller: int, port_streaming: int, all_client_info_list: List[ClientInfo]):
        """Initializes the server.

        Args:
            port_controller: The port of the controller server.
            port_streaming: The port of the streaming server.
            all_client_info_list: The information of the clients.
        """

        all_client_token_list = [client_info.token for client_info in all_client_info_list]

        self._is_callback_registered: bool = False
        self._controller_network_server: INetworkServer = HttpServer(
            port_controller, all_client_token_list)
        self._streaming_network_server: INetworkServer = HttpServer(
            port_streaming, all_client_token_list)

        # Game information
        self._game_info: GameInfo | None = None

        # Client information
        self._all_client_info: Dict[str, ClientInfo] = {
            client_info.token: client_info for client_info in all_client_info_list
        }

    async def start(self) -> None:
        """Starts the game."""

        if not self._is_callback_registered:
            await self._controller_network_server.register_callback(self._controller_callback)
            self._is_callback_registered = True

        await self._controller_network_server.start()
        await self._streaming_network_server.start()

    async def stop(self) -> None:
        """Stops the game."""

        await self._controller_network_server.stop()
        await self._streaming_network_server.stop()

    async def get_game_info(self) -> GameInfo:
        """Gets the information of the game.

        Returns:
            The information of the game.
        """

        if self._game_info is None:
            raise Exception("The game information is not ready.")

        return self._game_info
    
    async def set_game_info(self, game_info: GameInfo):
        """Sets the information of the game.

        Args:
            game_info: The information of the game.
        """

        self._game_info = game_info

    async def push_captured_image(self, token: str, image: np.ndarray) -> None:
        """Pushes the captured image to the client.

        Args:
            token: The token of the client.
            image: The captured image.
        """

        await self._streaming_network_server.send(Message({
            'type': 'push_captured_image',
            'bound_to': 'client',
            'data': image.tobytes(),
            'shape': list(image.shape),
        }), token)

    async def _controller_callback(self, client_token: str, message: Message) -> None:
        try:
            message_bound_to: str = message.get_bound_to()

            # Filter out the messages bound to the client
            if message_bound_to == 'client':
                return

            message_type = message.get_type()

            if message_type == 'get_game_info':
                if self._game_info is None:
                    raise Exception("The game information is not ready.")

                if self._all_client_info.get(client_token, None) is None or \
                        self._game_info.score.get(self._all_client_info[client_token].team, None) is None:
                    raise Exception("The client is not in the game.")

                await self._controller_network_server.send(Message({
                    'type': 'get_game_info',
                    'bound_to': 'client',
                    'stage': self._game_info.stage.value,
                    'start_time': self._game_info.start_time.timestamp(),
                    'end_time': self._game_info.end_time.timestamp(),
                    'score': self._game_info.score,
                    'simulation_rate': self._game_info.simulation_rate
                }), client_token)

            elif message_type == 'push_robot_control':
                # TODO: Implement this
                pass

        except Exception as e:
            self._logger.error(f"Failed to handle message: {e}")
