from security.policy_engine import PolicyEngine


class SecureAgent:
    """
    Wrapper de seguridad para un agente robótico.

    Intercepta las llamadas a herramientas antes de permitir
    que se ejecuten.
    """

    def __init__(self, agent):
        self.agent = agent
        self.policy_engine = PolicyEngine()

    def execute_tool(self, tool_name, arguments=None):
        """
        Comprueba los permisos antes de ejecutar una herramienta.
        """

        allowed, reason = self.policy_engine.check_tool(
            tool_name,
            arguments,
        )

        if not allowed:
            print(f"[SECURITY] Execution blocked: {reason}")
            return {
                "success": False,
                "blocked": True,
                "reason": reason,
            }

        print(f"[SECURITY] Execution allowed: {tool_name}")

        # La ejecución real dependerá de cómo el framework
        # exponga sus herramientas.
        if not hasattr(self.agent, "execute_tool"):
            raise NotImplementedError(
                "The underlying agent does not expose execute_tool(). "
                "Connect this wrapper to the framework's tool executor."
            )

        result = self.agent.execute_tool(
            tool_name,
            arguments or {},
        )

        return {
            "success": True,
            "blocked": False,
            "result": result,
        }
