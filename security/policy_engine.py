import math


class PolicyEngine:
    """
    Motor de políticas para controlar las herramientas
    que puede ejecutar el agente.
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

        # Herramientas autorizadas y sus argumentos.
        self.allowed_tools = {
            "navigate_to",
            "get_robot_position",
            "get_robot_status",
        }

        # Herramientas que nunca deben ejecutarse.
        self.blocked_tools = {
            "execute_shell",
            "run_terminal_command",
            "delete_files",
        }

    def check_tool(self, tool_name, arguments=None):
        """
        Comprueba si una herramienta puede ejecutarse.

        Returns:
            (bool, str): decisión y motivo.
        """

        # 1. Comprobar que el nombre es válido.
        if not isinstance(tool_name, str):
            return False, "Invalid tool name"

        # 2. Bloquear herramientas explícitamente prohibidas.
        if tool_name in self.blocked_tools:
            return False, f"Tool explicitly blocked: {tool_name}"

        # 3. Comprobar la lista de herramientas autorizadas.
        if tool_name not in self.allowed_tools:
            return False, f"Tool not authorized: {tool_name}"

        # 4. Comprobar los argumentos.
        if arguments is None:
            arguments = {}

        if not isinstance(arguments, dict):
            return False, "Tool arguments must be a dictionary"

        # 5. Validar los argumentos de cada herramienta.
        if tool_name == "navigate_to":

            required_arguments = {"x", "y"}

            if set(arguments.keys()) != required_arguments:
                return False, (
                    "navigate_to requires exactly two arguments: x and y"
                )

            x = arguments["x"]
            y = arguments["y"]

            # Evitar valores que no sean números.
            if isinstance(x, bool) or not isinstance(x, (int, float)):
                return False, "Invalid X coordinate"

            if isinstance(y, bool) or not isinstance(y, (int, float)):
                return False, "Invalid Y coordinate"

            # Comprobar que las coordenadas son finitas.
            try:
                if not math.isfinite(x) or not math.isfinite(y):
                    return False, "Coordinates must be finite"
            except (OverflowError, TypeError):
                return False, "Invalid coordinates"

            # Comprobar los límites permitidos.
            if not self.min_x <= x <= self.max_x:
                return False, "X coordinate outside allowed boundaries"

            if not self.min_y <= y <= self.max_y:
                return False, "Y coordinate outside allowed boundaries"

        elif tool_name in {
            "get_robot_position",
            "get_robot_status",
        }:

            if arguments:
                return False, "This tool does not accept arguments"

        return True, "Tool authorized"
