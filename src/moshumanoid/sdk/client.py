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

        self._is_callback_registered: bool = False
        self._network_client: INetworkClient = HttpClient(host, port, token)
        self._task_list: List[asyncio.Task] = []

        # Game information
        self._stage: GameStageKind | None = None
        self._start_time: datetime.datetime | None = None
        self._end_time: datetime.datetime | None = None
        self._score: Dict[str, float] = {}
        self._simulation_rate: float | None = None

        # Team information
        self._team: str | None = None

    async def connect(self) -> None:
        """Connects to the server."""

        if not self._is_callback_registered:
            await self._network_client.register_callback(self._callback)
            self._is_callback_registered = True

        await self._network_client.connect()

        self._task_list.append(asyncio.create_task(self._loop()))

    async def disconnect(self) -> None:
        """Disconnects from the server."""

        for task in self._task_list:
            task.cancel()

        self._task_list.clear()

        await self._network_client.disconnect()

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

    async def get_simulation_rate(self) -> float | None:
        """Gets the simulation rate.

        Returns:
            The simulation rate.
        """

        return self._simulation_rate

    async def _callback(self, msg: Message) -> None:
        try:
            message_bound_to: str = msg.get_bound_to()

            if message_bound_to == 'server':
                return

            message_type: str = msg.get_type()

            if message_type == 'get_game_info':
                self._stage = GameStageKind(str(msg.to_dict()['stage']))
                self._start_time = datetime.datetime.fromtimestamp(
                    int(msg.to_dict()['start_time']))
                self._end_time = datetime.datetime.fromtimestamp(
                    int(msg.to_dict()['end_time']))
                for score_item in msg.to_dict()['score']:
                    self._score[str(score_item['team'])] = float(
                        score_item['score'])
                self._simulation_rate = float(msg.to_dict()['simulation_rate'])

            elif message_type == 'get_team_info':
                self._team = str(msg.to_dict()['team'])

        except Exception as e:
            self._logger.error(f'Failed to handle message: {e}')

    async def _loop(self) -> None:
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
