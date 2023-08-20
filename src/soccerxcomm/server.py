from __future__ import annotations

from typing import Any, Callable, Coroutine, Dict, List

import numpy as np

from .game_info import GameInfo
from .http_server import HttpServer
from .logger import Logger
from .message import Message
from .network_server_interface import INetworkServer
from .robot_status import RobotStatus
from .robot_control import RobotControl


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

    def __init__(self, port_controller: int, port_streaming: int, client_team_map: Dict[str, str]):
        """Initializes the server.

        Args:
            port_controller: The port of the controller server.
            port_streaming: The port of the streaming server.
            client_team_map: The map of the client and the team.
        """

        self._client_team_map: Dict[str, str] = client_team_map
        self._is_callback_registered: bool = False
        self._robot_control_callback_list: List[Callable[[str, RobotControl], Coroutine[Any, Any, None]]] = []

        # Components
        self._controller_network_server: INetworkServer = HttpServer(
            port_controller, list(client_team_map.keys()))
        self._streaming_network_server: INetworkServer = HttpServer(
            port_streaming, list(client_team_map.keys()))
        
        # Game data
        self._game_info: GameInfo | None = None

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

    async def get_game_info(self) -> GameInfo | None:
        """Gets the information of the game.

        Returns:
            The information of the game.
        """

        return self._game_info
    
    async def set_game_info(self, game_info: GameInfo | None):
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

    async def push_robot_status(self, token: str, robot_status: RobotStatus) -> None:
        """Pushes the status of the robot to the client.

        Args:
            token: The token of the client.
            robot_status: The status of the robot.
        """

        await self._controller_network_server.send(Message({
            'type': 'push_robot_status',
            'bound_to': 'client',
            'head': {
                'head_angle': robot_status.head_angle,
                'neck_angle': robot_status.neck_angle
            },
            'imu': {
                'acceleration': {
                    'x': robot_status.acceleration[0],
                    'y': robot_status.acceleration[1],
                    'z': robot_status.acceleration[2]
                },
                'angular_velocity': {
                    'pitch': robot_status.angular_velocity[0],
                    'yaw': robot_status.angular_velocity[1],
                    'roll': robot_status.angular_velocity[2]
                },
                'attitude_angle': {
                    'pitch': robot_status.attitude_angle[0],
                    'yaw': robot_status.attitude_angle[1],
                    'roll': robot_status.attitude_angle[2]
                }
            },
            'team': robot_status.team
        }), token)

    async def register_robot_control_callback(self, callback: Callable[[str, RobotControl], Coroutine[Any, Any, None]]) -> None:
        """Registers a callback for the robot control.

        Args:
            callback: The callback.
        """

        self._robot_control_callback_list.append(callback)

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

                if self._client_team_map.get(client_token, None) is None or \
                        self._game_info.score.get(self._client_team_map[client_token], None) is None:
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
                obj = message.to_dict()

                head = None
                movement = None
                kick = None

                if obj.get('head', None) is not None:
                    head = RobotControl.Head(
                        head_angle=obj['head'].get('head_angle', None),
                        neck_angle=obj['head'].get('neck_angle', None)
                    )

                if obj.get('movement', None) is not None:
                    movement = RobotControl.Movement(
                        x=obj['movement'].get('x', None),
                        y=obj['movement'].get('y', None),
                        omega_z=obj['movement'].get('omega_z', None)
                    )

                if obj.get('kick', None) is not None:
                    kick = RobotControl.Kick(
                        x=obj['kick']['x'],
                        y=obj['kick']['y'],
                        z=obj['kick']['z'],
                        speed=obj['kick']['speed'],
                        delay=obj['kick']['delay']
                    )

                for callback in self._robot_control_callback_list:
                    await callback(client_token, RobotControl(head, movement, kick))

        except Exception as e:
            self._logger.error(f"Failed to handle message: {e}")
