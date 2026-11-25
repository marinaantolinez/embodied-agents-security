import numpy as np

from geometry_msgs.msg import PoseStamped as ROSPoseStamped
from ros_sugar.io.supported_types import (
    PoseStamped,
    add_additional_datatypes,
)


class SecurePoseStamped(PoseStamped):
    """
    A secure version of PoseStamped that validates the input data.

    Format:
        [x, y, z]
        [x, y, z, qw, qx, qy, qz]
    """

    _ros_type = ROSPoseStamped

    @classmethod
    def convert(cls, output, **kwargs) -> ROSPoseStamped:

        coordinates = np.asarray(output, dtype=np.float64)

        # Check dimensions
        if coordinates.ndim != 1 or len(coordinates) not in (3, 7):
            raise ValueError(
                "Exactly 3 or 7 coordinates are required."
            )

        # Reject non-finite values
        if not np.all(np.isfinite(coordinates)):
            raise ValueError(
                "Coordinates contain non-finite values."
            )

        msg = ROSPoseStamped()

        msg.pose.position.x = float(coordinates[0])
        msg.pose.position.y = float(coordinates[1])
        msg.pose.position.z = float(coordinates[2])

        if len(coordinates) == 3:
            # If only position is provided, set a default orientation (no rotation)
            msg.pose.orientation.w = 1.0
            msg.pose.orientation.x = 0.0
            msg.pose.orientation.y = 0.0
            msg.pose.orientation.z = 0.0

        else:
            qw, qx, qy, qz = coordinates[3:7]

            quaternion_norm = np.linalg.norm(
                [qw, qx, qy, qz]
            )

            if abs(quaternion_norm - 1.0) > 0.01:
                raise ValueError(
                    "El cuaternión no está normalizado."
                )

            msg.pose.orientation.w = float(qw)
            msg.pose.orientation.x = float(qx)
            msg.pose.orientation.y = float(qy)
            msg.pose.orientation.z = float(qz)

        # Reference frame required by GoalValidator
        msg.header.frame_id = "map"

        return msg


# Register the SecurePoseStamped type so that Topic can recognize it
add_additional_datatypes([SecurePoseStamped])
