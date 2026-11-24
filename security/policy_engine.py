import math


class PolicyEngine:
    """
    Policy engine for controlling the tools
    that the agent can execute.
    """

    def __init__(
        self,
        min_x=-5.0,
        max_x=5.0,
        min_y=-5.0,
        max_y=5.0,
    ):
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

        self.allowed_tools = {
            "navigate_to",
            "get_coordinates",
            "get_robot_position",
            "get_robot_status",
        }

        self.blocked_tools = {
            "execute_shell",
            "run_terminal_command",
            "delete_files",
        }

    def _valid_number(self, value):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return False

        try:
            return math.isfinite(value)
        except (OverflowError, TypeError):
            return False

    def check_tool(self, tool_name, arguments=None):
        if not isinstance(tool_name, str):
            return False, "Invalid tool name"

        if tool_name in self.blocked_tools:
            return False, f"Tool explicitly blocked: {tool_name}"

        if tool_name not in self.allowed_tools:
            return False, f"Tool not authorized: {tool_name}"

        if arguments is None:
            arguments = {}

        if not isinstance(arguments, dict):
            return False, "Tool arguments must be a dictionary"

        if tool_name == "get_coordinates":
            if set(arguments.keys()) != {"position"}:
                return False, "get_coordinates requires exactly one argument: position"

            position = arguments["position"]

            if not isinstance(position, (list, tuple)) or len(position) != 3:
                return False, "Position must contain exactly three coordinates"

            x, y, z = position

            if not all(self._valid_number(v) for v in position):
                return False, "Coordinates must be finite numbers"

            if not self.min_x <= x <= self.max_x:
                return False, "X coordinate outside allowed boundaries"

            if not self.min_y <= y <= self.max_y:
                return False, "Y coordinate outside allowed boundaries"

        elif tool_name == "navigate_to":
            if set(arguments.keys()) != {"x", "y"}:
                return False, "navigate_to requires exactly two arguments: x and y"

            x = arguments["x"]
            y = arguments["y"]

            if not self._valid_number(x):
                return False, "Invalid X coordinate"

            if not self._valid_number(y):
                return False, "Invalid Y coordinate"

            if not self.min_x <= x <= self.max_x:
                return False, "X coordinate outside allowed boundaries"

            if not self.min_y <= y <= self.max_y:
                return False, "Y coordinate outside allowed boundaries"

        elif tool_name in {"get_robot_position", "get_robot_status"}:
            if arguments:
                return False, "This tool does not accept arguments"

        return True, "Tool authorized"