import inspect
from functools import wraps

from security.policy_engine import PolicyEngine


class SecureAgent:
    """
    Interceptor de seguridad para las herramientas de EmbodiedAgents.
    """

    def __init__(self, agent=None, policy_engine=None):
        self.agent = agent
        self.policy_engine = policy_engine or PolicyEngine()
        self.audit_log = []

    def _register_event(
        self,
        tool_name,
        arguments,
        allowed,
        reason,
        executed=False,
    ):
        """Registra los intentos de ejecución."""

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
        Envuelve una herramienta para comprobar sus permisos
        antes de ejecutar la función original.
        """

        if not callable(tool_function):
            raise TypeError("tool_function debe ser una función.")

        @wraps(tool_function)
        def protected_tool(*args, **kwargs):

            # Recuperar y comprobar los argumentos.
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

            # Evaluar las políticas.
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

            # Ejecutar la función autorizada.
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

                # Fallo controlado: evitar publicar el resultado original.
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
        Registra una herramienta protegida directamente
        en un componente LLM de EmbodiedAgents.
        """

        function_description = tool_description.get("function", {})
        tool_name = function_description.get("name")

        if not isinstance(tool_name, str) or not tool_name:
            raise ValueError(
                "La descripción debe incluir function.name."
            )

        protected_tool = self.wrap_tool(
            tool_name,
            tool,
        )

        component.register_tool(
            tool=protected_tool,
            tool_description=tool_description,
            send_tool_response_to_model=send_tool_response_to_model,
        )

        return protected_tool

    def get_audit_log(self):
        """Devuelve una copia del registro de auditoría."""

        return list(self.audit_log)