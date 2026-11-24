class ToolRegistry:
    """
    A simple registry to keep track of registered tools.
    """

    def __init__(self):
        self._tools = set()

    def register(self, tool_name):
        if not isinstance(tool_name, str) or not tool_name:
            raise ValueError("Invalid tool name")

        if tool_name in self._tools:
            raise ValueError(
                f"Tool already registered: {tool_name}"
            )

        self._tools.add(tool_name)

    def is_registered(self, tool_name):
        return tool_name in self._tools

    def get_registered_tools(self):
        return set(self._tools)

    def unregister(self, tool_name):
        # Remove a tool from the registry if it exists
        self._tools.discard(tool_name)