import inspect
from functools import wraps

from security.policy_engine import PolicyEngine
from security.tool_registry import ToolRegistry


class SecureAgent:
    """
    Wrapper that enforces security policies on agent tool executions.
    It maintains a registry of tools and an audit log of execution attempts.
    """

    def __init__(self, agent=None, policy_engine=None):
        self.agent = agent
        self.policy_engine = policy_engine or PolicyEngine()
        self.tool_registry = ToolRegistry()
        self.audit_log = []

    def _register_event(
        self,
        tool_name,
        arguments,
        allowed,
        reason,
        executed=False,
    ):
        event = {
            "tool": tool_name,
            "arguments": dict(arguments),
            "allowed": allowed,
            "reason": reason,
            "executed": executed,
        }

        self.audit_log.append(event)

    def wrap_tool(self, tool_name, tool_function):
        """
        Register and wrap a tool with security checks.
        """

        if not isinstance(tool_name, str) or not tool_name:
            raise ValueError("Invalid tool name")

        if not callable(tool_function):
            raise TypeError("tool_function debe ser una función.")

        # Register the tool before creating its protected wrapper.
        self.tool_registry.register(tool_name)

        @wraps(tool_function)
        def protected_tool(*args, **kwargs):

            # Retrieve and verify the arguments.
            try:
                signature = inspect.signature(tool_function)
                bound = signature.bind(*args, **kwargs)
                bound.apply_defaults()

                arguments = dict(bound.arguments)

            except TypeError as error:
                reason = f"Invalid tool arguments: {error}"

                self._register_event(
                    tool_name, {}, False, reason
                )

                print(f"[SECURITY] BLOCKED: {tool_name} - {reason}")
                return None

            # Check whether the tool is registered.
            if not self.tool_registry.is_registered(tool_name):
                reason = "Tool is not registered"

                self._register_event(
                    tool_name,
                    arguments,
                    False,
                    reason,
                )

                print(f"[SECURITY] BLOCKED: {tool_name} - {reason}")
                return None

            # Evaluate the security policy.
            try:
                allowed, reason = self.policy_engine.check_tool(
                    tool_name,
                    arguments,
                )

            except Exception as error:
                allowed = False
                reason = f"Policy evaluation failed: {error}"

            if not allowed:
                self._register_event(
                    tool_name,
                    arguments,
                    False,
                    reason,
                )

                print(f"[SECURITY] BLOCKED: {tool_name} - {reason}")
                return None

            # Execute the authorized function.
            try:
                result = tool_function(*args, **kwargs)

            except Exception as error:
                reason = f"Tool execution failed: {error}"

                self._register_event(
                    tool_name,
                    arguments,
                    True,
                    reason,
                    executed=False,
                )

                print(f"[SECURITY] ERROR: {tool_name} - {reason}")
                return None

            self._register_event(
                tool_name,
                arguments,
                True,
                "Tool authorized",
                executed=True,
            )

            print(f"[SECURITY] ALLOWED: {tool_name}")

            return result

        return protected_tool

    def register_tool(
        self,
        component,
        tool,
        tool_description,
        send_tool_response_to_model=False,
    ):
        """
        Register a protected tool in an external component.
        """

        function_description = tool_description.get("function", {})
        tool_name = function_description.get("name")

        if not isinstance(tool_name, str) or not tool_name:
            raise ValueError(
                "The description must include function.name."
            )

        protected_tool = self.wrap_tool(
            tool_name,
            tool,
        )

        try:
            component.register_tool(
                tool=protected_tool,
                tool_description=tool_description,
                send_tool_response_to_model=send_tool_response_to_model,
            )

        except Exception:
            self.tool_registry.unregister(tool_name)
            raise

        return protected_tool

    def get_audit_log(self):
        return list(self.audit_log)