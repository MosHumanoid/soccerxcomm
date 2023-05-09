from __future__ import annotations

import datetime
from typing import Dict

from .game_stage_kind import GameStageKind
from .http_server import HttpServer
from .logger import Logger
from .message import Message
from .network_server import INetworkServer


class Server:
    """The MosHumanoid server."""

    class ClientInfo:
        """The information of the client."""

        def __init__(self, team: str, token: str):
            """Initializes the information of the client.

            Args:
                team: The name of the team.
                token: The token of the client.
            """

            self.team: str = team
            self.token: str = token

    _logger = Logger("Server")

    def __init__(self, port: int, all_client_info: Dict[str, Server.ClientInfo]):
        """Initializes the server.

        Args:
            port: The port of the server.
            all_client_info: The information of the clients.
        """

        self._network_server: INetworkServer = HttpServer(
            port, list(all_client_info.keys()))
        self._all_client_info: Dict[str, Server.ClientInfo] = all_client_info

        self._network_server.register_callback(self._callback).__await__()
        self._network_server.start().__await__()

        # Game information
        self._stage: GameStageKind | None = None
        self._start_time: datetime.datetime | None = None
        self._end_time: datetime.datetime | None = None
        self._score: Dict[str, float] = {}  # team -> score

    def __del__(self):
        """Destructs the server."""

        self._network_server.stop().__await__()

    async def get_stage(self) -> GameStageKind | None:
        """Gets the current stage of the game.

        Returns:
            The current stage of the game.
        """

        return self._stage

    async def set_stage(self, stage: GameStageKind) -> None:
        """Sets the current stage of the game.

        Args:
            stage: The current stage of the game.
        """

        self._stage = stage

    async def get_start_time(self) -> datetime.datetime | None:
        """Gets the start time of the game.

        Returns:
            The start time of the game.
        """

        return self._start_time

    async def set_start_time(self, start_time: datetime.datetime) -> None:
        """Sets the start time of the game.

        Args:
            start_time: The start time of the game.
        """

        self._start_time = start_time

    async def get_end_time(self) -> datetime.datetime | None:
        """Gets the end time of the game.

        Returns:
            The end time of the game.
        """

        return self._end_time

    async def set_end_time(self, end_time: datetime.datetime) -> None:
        """Sets the end time of the game.

        Args:
            end_time: The end time of the game.
        """

        self._end_time = end_time

    async def get_score(self, team: str) -> float | None:
        """Gets the score of the team.

        Args:
            team: The name of the team.

        Returns:
            The score of the team.
        """

        return self._score.get(team, None)

    async def set_score(self, team: str, score: float) -> None:
        """Sets the score of the team.

        Args:
            team: The name of the team.
            score: The score of the team.
        """

        self._score[team] = score

    async def _callback(self, client_token: str, message: Message) -> None:
        try:
            message_type = message.get_type()

            if message_type == 'get_game_info':
                if self._stage is None or self._start_time is None or \
                        self._end_time is None or self._score is None:
                    raise Exception("The game information is not ready.")

                if self._all_client_info.get(client_token, None) is None or \
                        self._score.get(self._all_client_info[client_token].team, None) is None:
                    raise Exception("The client is not in the game.")

                await self._network_server.send(Message({
                    'type': 'get_game_info',
                    'bound_to': 'client',
                    'stage': self._stage.value,
                    'start_time': self._start_time.timestamp(),
                    'end_time': self._end_time.timestamp(),
                    'score': self._score[self._all_client_info[client_token].team]
                }), client_token)

            elif message_type == 'get_team_info':
                if self._all_client_info.get(client_token, None) is None:
                    raise Exception("The client is not in the game.")

                await self._network_server.send(Message({
                    'type': 'get_team_info',
                    'bound_to': 'client',
                    'team': self._all_client_info[client_token].team
                }), client_token)

        except Exception as e:
            self._logger.error(f"Failed to handle message: {e}")
