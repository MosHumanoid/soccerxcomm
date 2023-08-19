from __future__ import annotations

import asyncio
import datetime
from typing import Any, Dict, List

import numpy as np

from .game_info import GameInfo
from .game_stage_kind import GameStageKind
from .http_client import HttpClient
from .logger import Logger
from .message import Message
from .network_client_interface import INetworkClient
from .robot_control import RobotControl
from .robot_status import RobotStatus


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

        self._game_info: GameInfo | None = None
        self._robot_status: RobotStatus | None = None

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

    async def get_captured_image(self) -> np.ndarray | None:
        """Gets the captured image.

        Returns:
            The captured image.
        """

        return self._captured_image

    async def get_game_info(self) -> GameInfo | None:
        """Gets the game information.

        Returns:
            The game information.
        """

        return self._game_info

    async def get_robot_status(self) -> RobotStatus | None:
        """Gets the robot status.

        Returns:
            The robot status.
        """

        return self._robot_status

    async def push_robot_control(self, robot_control: RobotControl) -> None:
        """Pushes the control of the robot to the server.

        Args:
            robot_control: The control of the robot.
        """

        obj: Dict[str, Any] = {
            'type': 'push_robot_control',
            'bound_to': 'server',
        }

        if robot_control.head is not None:
            obj['head'] = {}
            if robot_control.head.head_angle is not None:
                obj['head']['head_angle'] = robot_control.head.head_angle
            if robot_control.head.neck_angle is not None:
                obj['head']['neck_angle'] = robot_control.head.neck_angle

        if robot_control.movement is not None:
            obj['movement'] = {}
            if robot_control.movement.x is not None:
                obj['movement']['x'] = robot_control.movement.x
            if robot_control.movement.y is not None:
                obj['movement']['y'] = robot_control.movement.y
            if robot_control.movement.omega_z is not None:
                obj['movement']['omega_z'] = robot_control.movement.omega_z

        if robot_control.kick is not None:
            obj['kick'] = {}
            obj['kick']['x'] = robot_control.kick.x
            obj['kick']['y'] = robot_control.kick.y
            obj['kick']['z'] = robot_control.kick.z
            obj['kick']['speed'] = robot_control.kick.speed
            obj['kick']['delay'] = robot_control.kick.delay

        await self._controller_network_client.send(Message(obj))

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
                self._robot_status = RobotStatus(
                    head_angle=float(msg.to_dict()['head']['head_angle']),
                    neck_angle=float(msg.to_dict()['head']['neck_angle']),
                    acceleration=np.array([
                        float(msg.to_dict()['imu']['acceleration']['x']),
                        float(msg.to_dict()['imu']['acceleration']['y']),
                        float(msg.to_dict()['imu']['acceleration']['z']),
                    ]),
                    angular_velocity=np.array([
                        float(msg.to_dict()['imu']
                              ['angular_velocity']['pitch']),
                        float(msg.to_dict()['imu']['angular_velocity']['yaw']),
                        float(msg.to_dict()['imu']
                              ['angular_velocity']['roll']),
                    ]),
                    attitude_angle=np.array([
                        float(msg.to_dict()['imu']['attitude_angle']['pitch']),
                        float(msg.to_dict()['imu']['attitude_angle']['yaw']),
                        float(msg.to_dict()['imu']['attitude_angle']['roll']),
                    ]),
                    team=msg.to_dict()['team']
                )

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
