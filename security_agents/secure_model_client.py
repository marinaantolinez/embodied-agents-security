from collections.abc import Mapping
from typing import Any, Dict, Optional

from agents.clients.model_base import ModelClient

from security.tool_registry import ToolRegistry


class SecureModelClient(ModelClient):
    """
    Security wrapper around an existing ModelClient.

    It delegates model operations to the original client and filters
    tool calls that are not present in the shared ToolRegistry.
    """

    def __init__(
        self,
        model_client: ModelClient,
        tool_registry: ToolRegistry,
    ):
        if model_client is None:
            raise ValueError("model_client cannot be None")

        if tool_registry is None:
            raise ValueError("tool_registry cannot be None")

        self.model_client = model_client
        self.tool_registry = tool_registry
        self.audit_log = []

        # Reuse the configuration of the wrapped client.
        client_config = model_client.serialize()

        super().__init__(
            model=client_config["model"],
            host=client_config["host"],
            port=client_config["port"],
            inference_timeout=client_config["inference_timeout"],
            init_on_activation=client_config["init_on_activation"],
            logging_level=client_config["logging_level"],
            ca_cert=client_config["ca_cert"],
        )
    
    @property
    def supports_tool_calls(self) -> bool:
        """Delegate tool-calling capability to the wrapped client."""
        return self.model_client.supports_tool_calls

    @property
    def supports_decisions(self) -> bool:
        """Delegate decision-model capability to the wrapped client."""
        return self.model_client.supports_decisions

    def _check_connection(self) -> None:
        self.model_client.check_connection()

    def _initialize(self) -> None:
        self.model_client.initialize()

    def _deinitialize(self) -> None:
        self.model_client.deinitialize()

    def _inference(
        self,
        inference_input: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:

        result = self.model_client.inference(inference_input)

        if result is None:
            return None

        if not isinstance(result, Mapping):
            return result

        # Do not modify the original response returned by the model client.
        secure_result = dict(result)

        tool_calls = secure_result.get("tool_calls")

        # No tool calls: return the model response unchanged.
        if tool_calls is None:
            return secure_result

        if not isinstance(tool_calls, list):
            self._record_rejection(
                tool_name=None,
                reason="Malformed tool_calls structure",
            )
            secure_result.pop("tool_calls", None)
            return secure_result

        accepted_calls = []

        for tool_call in tool_calls:
            if not isinstance(tool_call, Mapping):
                self._record_rejection(
                    tool_name=None,
                    reason="Malformed tool call",
                )
                continue

            function = tool_call.get("function")

            if not isinstance(function, Mapping):
                self._record_rejection(
                    tool_name=None,
                    reason="Missing or malformed function definition",
                )
                continue

            tool_name = function.get("name")

            if not isinstance(tool_name, str) or not tool_name:
                self._record_rejection(
                    tool_name=None,
                    reason="Missing or invalid tool name",
                )
                continue

            if not self.tool_registry.is_registered(tool_name):
                self._record_rejection(
                    tool_name=tool_name,
                    reason="Tool is not registered",
                )
                continue

            accepted_calls.append(tool_call)

        if accepted_calls:
            secure_result["tool_calls"] = accepted_calls
        else:
            secure_result.pop("tool_calls", None)

        return secure_result

    def _record_rejection(
        self,
        tool_name: Optional[str],
        reason: str,
    ) -> None:
        event = {
            "tool": tool_name,
            "allowed": False,
            "executed": False,
            "reason": reason,
        }

        self.audit_log.append(event)

        self.logger.warning(
            f"[SECURITY] BLOCKED tool call: {tool_name} - {reason}"
        )

    def get_audit_log(self) -> list:
        return list(self.audit_log)