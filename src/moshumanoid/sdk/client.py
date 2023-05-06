from __future__ import annotations

import asyncio
import datetime
from typing import Dict, List

from .game_stage_kind import GameStageKind
from .http_client import HttpClient
from .logger import Logger
from .message import Message
from .network_client import INetworkClient


class Client:
    """The client to send commands to the server."""

    _logger = Logger("Client")

    def __init__(self, host: str, port: int, token: str):
        """Initializes the client.

        Args:
            host: The server address.
            port: The server port.
            token: The token of the game.
        """

        self._network_client: INetworkClient = HttpClient(host, port, token)
        self._token: str = token

        self._network_client.register_callback(self._callback).__await__()
        self._task_list: List[asyncio.Task] = [
            asyncio.create_task(self._loop())
        ]

        # Game information
        self._stage: GameStageKind | None = None
        self._start_time: datetime.datetime | None = None
        self._end_time: datetime.datetime | None = None
        self._score: Dict[str, float] = {}

        # Team information
        self._team: str | None = None

    async def get_token(self) -> str:
        """Gets the token of the game.

        Returns:
            The token of the game.
        """

        return self._token
    
    async def get_stage(self) -> GameStageKind | None:
        """Gets the current stage of the game.

        Returns:
            The current stage of the game.
        """

        return self._stage
    
    async def get_start_time(self) -> datetime.datetime | None:
        """Gets the start time of the game.

        Returns:
            The start time of the game.
        """

        return self._start_time
    
    async def get_end_time(self) -> datetime.datetime | None:
        """Gets the end time of the game.

        Returns:
            The end time of the game.
        """

        return self._end_time
    
    async def get_score(self, team: str) -> float | None:
        """Gets the score of the team.

        Args:
            team: The team name.

        Returns:
            The score of the team.
        """

        return self._score.get(team, None)

    async def _callback(self, msg: Message) -> None:
        try:
            message_type: str = msg.get_type()

            if message_type == 'get_game_info':
                self._stage = GameStageKind(str(msg['stage']))
                self._start_time = datetime.datetime.fromtimestamp(int(msg['start_time']))
                self._end_time = datetime.datetime.fromtimestamp(int(msg['end_time']))
                for score_item in msg['score']:
                    self._score[str(score_item['team'])] = float(score_item['score'])

            elif message_type == 'get_team_info':
                self._team = str(msg['team'])

        except Exception as e:
            self._logger.error(f'Failed to handle message: {e}')

    async def _loop(self) -> None:
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
