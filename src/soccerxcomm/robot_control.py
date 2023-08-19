from __future__ import annotations


class RobotControl:
    """Robot control commands."""

    class Head:
        """Head control commands."""

        def __init__(self, head_angle: float | None = None, neck_angle: float | None = None):
            """Initializes the head control commands.

            Args:
                head_angle: The head angle in degrees.
                neck_angle: The neck angle in degrees.
            """

            self.head_angle: float | None = head_angle
            self.neck_angle: float | None = neck_angle

    class Movement:
        """Movement control commands."""

        def __init__(self, x: float | None = None, y: float | None = None, omega_z: float | None = None):
            """Initializes the movement control commands.

            Args:
                x: The x-axis velocity.
                y: The y-axis velocity.
                omega_z: The angular velocity around the z-axis.
            """

            self.x: float | None = x
            self.y: float | None = y
            self.omega_z: float | None = omega_z

    class Kick:
        """Kick control commands."""

        def __init__(self, x: float, y: float, z: float, speed: float, delay: float):
            """Initializes the kick control commands.

            Args:
                x: The x-axis velocity.
                y: The y-axis velocity.
                z: The z-axis velocity.
                speed: The speed of the kick.
                delay: The delay of the kick.
            """

            self.x: float = x
            self.y: float = y
            self.z: float = z
            self.speed: float = speed
            self.delay: float = delay

    def __init__(self, head: Head | None = None, movement: Movement | None = None, kick: Kick | None = None):
        """Initializes the robot control commands.

        Args:
            head: The head control commands.
            movement: The movement control commands.
            kick: The kick control commands.
        """

        self.head: RobotControl.Head | None = head
        self.movement: RobotControl.Movement | None = movement
        self.kick: RobotControl.Kick | None = kick
