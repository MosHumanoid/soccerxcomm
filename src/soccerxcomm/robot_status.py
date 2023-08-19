import numpy as np


class RobotStatus:
    """The status of the robot."""

    def __init__(self, head_angle: float, neck_angle: float, acceleration: np.ndarray, angular_velocity: np.ndarray, attitude_angle: np.ndarray, team: str):
        """Initializes the status of the robot.

        Args:
            head_angle: The angle of the head.
            neck_angle: The angle of the neck.
            acceleration: The acceleration of the robot.
            angular_velocity: The angular velocity of the robot.
            attitude_angle: The attitude angle of the robot.
            team: The team of the robot.
        """

        # Validate the shapes
        if acceleration.shape != (3,):
            raise Exception("The shape of the acceleration must be (3,).")
        if angular_velocity.shape != (3,):
            raise Exception("The shape of the angular velocity must be (3,).")
        if attitude_angle.shape != (3,):
            raise Exception("The shape of the attitude angle must be (3,).")

        self.head_angle: float = head_angle
        self.neck_angle: float = neck_angle
        self.acceleration: np.ndarray = acceleration
        self.angular_velocity: np.ndarray = angular_velocity
        self.attitude_angle: np.ndarray = attitude_angle
        self.team: str = team
