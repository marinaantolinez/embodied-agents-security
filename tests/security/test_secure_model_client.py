from security.tool_registry import ToolRegistry
from security_agents.secure_model_client import SecureModelClient


class FakeModelClient:
    def __init__(self):
        self.check_connection_called = False
        self.initialize_called = False
        self.deinitialize_called = False

        self.response = {
            "output": "Test response"
        }

    @property
    def supports_tool_calls(self):
        return True

    @property
    def supports_decisions(self):
        return False

    def serialize(self):
        return {
            "client_type": "FakeModelClient",
            "model": {
                "model_name": "fake-model",
                "model_type": "FakeModel",
                "init_timeout": None,
                "model_init_params": {},
            },
            "host": "127.0.0.1",
            "port": 11434,
            "init_on_activation": True,
            "logging_level": "INFO",
            "inference_timeout": 30,
            "ca_cert": None,
        }

    def check_connection(self):
        self.check_connection_called = True

    def initialize(self):
        self.initialize_called = True

    def deinitialize(self):
        self.deinitialize_called = True

    def inference(self, inference_input):
        return self.response


def create_secure_client():
    fake_client = FakeModelClient()
    registry = ToolRegistry()

    registry.register("get_coordinates")

    secure_client = SecureModelClient(
        model_client=fake_client,
        tool_registry=registry,
    )

    return secure_client, fake_client, registry


def test_registered_tool_is_preserved():
    secure_client, _, _ = create_secure_client()

    response = {
        "tool_calls": [
            {
                "function": {
                    "name": "get_coordinates",
                    "arguments": {"position": [1.0, 2.0, 0.0]},
                }
            }
        ],
        "output": "",
    }

    secure_client.model_client.response = response

    result = secure_client.inference({})

    assert len(result["tool_calls"]) == 1
    assert result["tool_calls"][0]["function"]["name"] == "get_coordinates"
    assert secure_client.get_audit_log() == []


def test_unknown_tool_is_filtered():
    secure_client, _, _ = create_secure_client()

    secure_client.model_client.response = {
        "tool_calls": [
            {
                "function": {
                    "name": "execute_shell",
                    "arguments": {"command": "test"},
                }
            }
        ],
        "output": "",
    }

    result = secure_client.inference({})

    assert "tool_calls" not in result

    audit = secure_client.get_audit_log()

    assert len(audit) == 1
    assert audit[0]["tool"] == "execute_shell"
    assert audit[0]["allowed"] is False
    assert audit[0]["executed"] is False


def test_mixed_tool_calls_only_preserve_registered_tools():
    secure_client, _, _ = create_secure_client()

    secure_client.model_client.response = {
        "tool_calls": [
            {
                "function": {
                    "name": "get_coordinates",
                    "arguments": {"position": [1.0, 2.0, 0.0]},
                }
            },
            {
                "function": {
                    "name": "unknown_tool",
                    "arguments": {},
                }
            },
        ],
        "output": "",
    }

    result = secure_client.inference({})

    assert len(result["tool_calls"]) == 1
    assert result["tool_calls"][0]["function"]["name"] == "get_coordinates"

    assert len(secure_client.get_audit_log()) == 1
    assert secure_client.get_audit_log()[0]["tool"] == "unknown_tool"


def test_response_without_tool_calls_is_preserved():
    secure_client, _, _ = create_secure_client()

    expected = {
        "output": "Hello",
    }

    secure_client.model_client.response = expected

    result = secure_client.inference({})

    assert result == expected
    assert secure_client.get_audit_log() == []


def test_malformed_tool_calls_structure_is_filtered():
    secure_client, _, _ = create_secure_client()

    secure_client.model_client.response = {
        "tool_calls": "not-a-list",
        "output": "",
    }

    result = secure_client.inference({})

    assert "tool_calls" not in result
    assert len(secure_client.get_audit_log()) == 1


def test_malformed_individual_tool_call_is_filtered():
    secure_client, _, _ = create_secure_client()

    secure_client.model_client.response = {
        "tool_calls": [
            {"invalid": "structure"},
            {
                "function": {
                    "name": "get_coordinates",
                    "arguments": {"position": [1.0, 2.0, 0.0]},
                }
            },
        ],
        "output": "",
    }

    result = secure_client.inference({})

    assert len(result["tool_calls"]) == 1
    assert result["tool_calls"][0]["function"]["name"] == "get_coordinates"
    assert len(secure_client.get_audit_log()) == 1


def test_lifecycle_methods_are_delegated():
    secure_client, fake_client, _ = create_secure_client()

    secure_client.check_connection()
    secure_client.initialize()
    secure_client.deinitialize()

    assert fake_client.check_connection_called is True
    assert fake_client.initialize_called is True
    assert fake_client.deinitialize_called is True


def test_audit_log_returns_a_copy():
    secure_client, _, _ = create_secure_client()

    secure_client.model_client.response = {
        "tool_calls": [
            {
                "function": {
                    "name": "unknown_tool",
                    "arguments": {},
                }
            }
        ]
    }

    secure_client.inference({})

    audit = secure_client.get_audit_log()
    audit.clear()

    assert len(secure_client.get_audit_log()) == 1


def test_unknown_tool_registered_afterwards_is_accepted():
    secure_client, _, registry = create_secure_client()

    registry.register("get_robot_status")

    secure_client.model_client.response = {
        "tool_calls": [
            {
                "function": {
                    "name": "get_robot_status",
                    "arguments": {},
                }
            }
        ],
        "output": "",
    }

    result = secure_client.inference({})

    assert len(result["tool_calls"]) == 1
    assert secure_client.get_audit_log() == []

def test_tool_call_capability_is_delegated():
    secure_client, _, _ = create_secure_client()

    assert secure_client.supports_tool_calls is True


def test_decision_capability_is_delegated():
    secure_client, _, _ = create_secure_client()

    assert secure_client.supports_decisions is False