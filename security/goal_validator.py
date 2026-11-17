import math


class GoalValidator:
    """
    Valida objetivos de navegación antes de permitir
    que se envíen al sistema robótico.
    """

    def __init__(
        self,
        min_x=-5.0,
        max_x=5.0,
        min_y=-5.0,
        max_y=5.0,
        expected_frame="map",
    ):

        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.expected_frame = expected_frame

    def validate(self, goal):
        """
        Recibe un geometry_msgs/PoseStamped.

        Returns:
            (bool, str): resultado de la validación y motivo.
        """

        # 1. Comprobar la estructura del mensaje.
        try:
            frame = goal.header.frame_id
            position = goal.pose.position
            orientation = goal.pose.orientation

        except AttributeError:
            return False, "Invalid goal message structure"

        # 2. Comprobar el sistema de referencia.
        if frame != self.expected_frame:
            return False, (
                f"Invalid frame: expected '{self.expected_frame}', "
                f"received '{frame}'"
            )

        # 3. Comprobar que las coordenadas son válidas.
        coordinates = [
            position.x,
            position.y,
            position.z,
        ]

        try:
            if not all(math.isfinite(value) for value in coordinates):
                return False, "Goal contains non-finite coordinates"

        except (TypeError, ValueError, OverflowError):
            return False, "Invalid coordinate values"

        # 4. Comprobar los límites de navegación.
        if not self.min_x <= position.x <= self.max_x:
            return False, "X coordinate outside allowed boundaries"

        if not self.min_y <= position.y <= self.max_y:
            return False, "Y coordinate outside allowed boundaries"

        # 5. Comprobar que la orientación es válida.
        quaternion = [
            orientation.x,
            orientation.y,
            orientation.z,
            orientation.w,
        ]

        try:
            if not all(math.isfinite(value) for value in quaternion):
                return False, "Orientation contains non-finite values"

            norm = math.sqrt(sum(value ** 2 for value in quaternion))

        except (TypeError, ValueError, OverflowError):
            return False, "Invalid quaternion values"

        if norm < 1e-6:
            return False, "Invalid quaternion: zero norm"

        if abs(norm - 1.0) > 0.01:
            return False, "Invalid quaternion: not normalized"

        return True, "Goal accepted"
