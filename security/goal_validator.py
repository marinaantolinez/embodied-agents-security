import math


class GoalValidator:
    """
    Validates navigation goals before allowing them to be sent
    to the robotic system.
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
        Receives a geometry_msgs/PoseStamped.

        Returns:
            (bool, str): validation result and reason.
        """

        # Check the structure of the PoseStamped message
        try:
            frame = goal.header.frame_id
            position = goal.pose.position
            orientation = goal.pose.orientation

        except AttributeError:
            return False, "Invalid goal message structure"

        # Check the reference frame
        if frame != self.expected_frame:
            return False, (
                f"Invalid frame: expected '{self.expected_frame}', "
                f"received '{frame}'"
            )

        # Check that the coordinates are valid
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

        # Check the navigation boundaries.
        if not self.min_x <= position.x <= self.max_x:
            return False, "X coordinate outside allowed boundaries"

        if not self.min_y <= position.y <= self.max_y:
            return False, "Y coordinate outside allowed boundaries"

        # Check that the orientation is valid.
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
