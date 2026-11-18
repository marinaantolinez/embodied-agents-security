import numpy as np

from geometry_msgs.msg import PoseStamped as ROSPoseStamped
from ros_sugar.io.supported_types import (
    PoseStamped,
    add_additional_datatypes,
)


class SecurePoseStamped(PoseStamped):
    """
    Conversor seguro de coordenadas a ROS PoseStamped.

    Formatos admitidos:
        [x, y, z]
        [x, y, z, qw, qx, qy, qz]
    """

    _ros_type = ROSPoseStamped

    @classmethod
    def convert(cls, output, **kwargs) -> ROSPoseStamped:

        coordinates = np.asarray(output, dtype=np.float64)

        # Comprobar dimensiones
        if coordinates.ndim != 1 or len(coordinates) not in (3, 7):
            raise ValueError(
                "Se requieren exactamente 3 o 7 coordenadas."
            )

        # Rechazar valores no finitos
        if not np.all(np.isfinite(coordinates)):
            raise ValueError(
                "Las coordenadas contienen valores no finitos."
            )

        msg = ROSPoseStamped()

        # Posición
        msg.pose.position.x = float(coordinates[0])
        msg.pose.position.y = float(coordinates[1])
        msg.pose.position.z = float(coordinates[2])

        if len(coordinates) == 3:
            # Orientación identidad
            msg.pose.orientation.w = 1.0
            msg.pose.orientation.x = 0.0
            msg.pose.orientation.y = 0.0
            msg.pose.orientation.z = 0.0

        else:
            # Orden: qw, qx, qy, qz
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

        # Marco de referencia requerido por GoalValidator
        msg.header.frame_id = "map"

        return msg


# Registrar el tipo para que Topic pueda reconocerlo
add_additional_datatypes([SecurePoseStamped])
