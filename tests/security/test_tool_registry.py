import pytest

from security.tool_registry import ToolRegistry


def test_register_tool():

    registry = ToolRegistry()

    registry.register("get_coordinates")

    assert registry.is_registered("get_coordinates")


def test_unknown_tool():

    registry = ToolRegistry()

    assert registry.is_registered("execute_shell") is False


def test_duplicate_registration():

    registry = ToolRegistry()

    registry.register("get_coordinates")

    with pytest.raises(ValueError):
        registry.register("get_coordinates")


def test_invalid_tool_name():

    registry = ToolRegistry()

    with pytest.raises(ValueError):
        registry.register("")


def test_unregister_tool():

    registry = ToolRegistry()

    registry.register("get_coordinates")
    registry.unregister("get_coordinates")

    assert registry.is_registered("get_coordinates") is False


def test_get_registered_tools():

    registry = ToolRegistry()

    registry.register("get_coordinates")
    registry.register("navigate_to")

    assert registry.get_registered_tools() == {
        "get_coordinates",
        "navigate_to",
    }