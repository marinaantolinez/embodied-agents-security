from security_agents.secure_agent import SecureAgent


def test_allowed_tool_is_executed():

    agent = SecureAgent()

    def get_coordinates(position: list[float]):
        return position

    protected_tool = agent.wrap_tool(
        "get_coordinates",
        get_coordinates,
    )

    result = protected_tool(position=[1.0, 2.0, 0.0])

    assert result == [1.0, 2.0, 0.0]

    assert agent.audit_log[-1]["allowed"] is True


def test_out_of_bounds_tool_is_blocked():

    agent = SecureAgent()

    executed = False

    def get_coordinates(position: list[float]):
        nonlocal executed
        executed = True
        return position

    protected_tool = agent.wrap_tool(
        "get_coordinates",
        get_coordinates,
    )

    result = protected_tool(position=[10.0, 2.0, 0.0])

    assert result is None
    assert executed is False

    assert agent.audit_log[-1]["allowed"] is False


def test_unknown_tool_is_blocked():

    agent = SecureAgent()

    executed = False

    def dangerous_tool():
        nonlocal executed
        executed = True
        return "executed"

    protected_tool = agent.wrap_tool(
        "execute_shell",
        dangerous_tool,
    )

    result = protected_tool()

    assert result is None
    assert executed is False

    assert agent.audit_log[-1]["allowed"] is False


def test_audit_log_records_calls():

    agent = SecureAgent()

    def get_coordinates(position: list[float]):
        return position

    protected_tool = agent.wrap_tool(
        "get_coordinates",
        get_coordinates,
    )

    protected_tool(position=[1.0, 2.0, 0.0])
    protected_tool(position=[20.0, 2.0, 0.0])

    log = agent.get_audit_log()

    assert len(log) == 2
    assert log[0]["allowed"] is True
    assert log[1]["allowed"] is False

def test_register_tool_registers_protected_function():

    class FakeLLM:

        def register_tool(
            self,
            tool,
            tool_description,
            send_tool_response_to_model=False,
        ):
            self.registered_tool = tool
            self.description = tool_description

    agent = SecureAgent()
    llm = FakeLLM()

    def get_coordinates(position: list[float]):
        return position

    description = {
        "type": "function",
        "function": {
            "name": "get_coordinates",
            "description": "Return robot coordinates",
            "parameters": {
                "type": "object",
                "properties": {
                    "position": {
                        "type": "array",
                        "items": {"type": "number"},
                    }
                },
                "required": ["position"],
            },
        },
    }

    agent.register_tool(
        component=llm,
        tool=get_coordinates,
        tool_description=description,
    )

    result = llm.registered_tool(
        position=[1.0, 2.0, 0.0]
    )

    assert result == [1.0, 2.0, 0.0]
    assert agent.audit_log[-1]["allowed"] is True
    assert agent.audit_log[-1]["executed"] is True


def test_tool_exception_does_not_escape():

    agent = SecureAgent()

    def failing_tool(position: list[float]):
        raise RuntimeError("Simulated tool failure")

    protected_tool = agent.wrap_tool(
        "get_coordinates",
        failing_tool,
    )

    result = protected_tool(
        position=[1.0, 2.0, 0.0]
    )

    assert result is None
    assert agent.audit_log[-1]["allowed"] is True
    assert agent.audit_log[-1]["executed"] is False

def test_tool_is_registered_when_wrapped():

    agent = SecureAgent()

    def get_coordinates(position: list[float]):
        return position

    agent.wrap_tool(
        "get_coordinates",
        get_coordinates,
    )

    assert agent.tool_registry.is_registered("get_coordinates")


def test_unregistered_tool_cannot_execute():

    agent = SecureAgent()

    executed = False

    def get_coordinates(position: list[float]):
        nonlocal executed
        executed = True
        return position

    protected_tool = agent.wrap_tool(
        "get_coordinates",
        get_coordinates,
    )

    # Remove the tool from the registry.
    agent.tool_registry.unregister("get_coordinates")

    result = protected_tool(
        position=[1.0, 2.0, 0.0]
    )

    assert result is None
    assert executed is False
    assert agent.audit_log[-1]["allowed"] is False
    assert agent.audit_log[-1]["executed"] is False
    assert agent.audit_log[-1]["reason"] == "Tool is not registered"


def test_duplicate_tool_registration_is_rejected():

    agent = SecureAgent()

    def get_coordinates(position: list[float]):
        return position

    agent.wrap_tool(
        "get_coordinates",
        get_coordinates,
    )

    try:
        agent.wrap_tool(
            "get_coordinates",
            get_coordinates,
        )
        assert False, "Expected duplicate registration to fail"

    except ValueError as error:
        assert "already registered" in str(error)