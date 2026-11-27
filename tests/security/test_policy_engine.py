import pytest
from security.policy_engine import PolicyEngine


def test_allowed_tool():

    policy = PolicyEngine()

    allowed, reason = policy.check_tool(
        "navigate_to",
        {"x": 1.0, "y": 2.0},
    )

    assert allowed is True


def test_unknown_tool():

    policy = PolicyEngine()

    allowed, reason = policy.check_tool(
        "unknown_tool",
        {},
    )

    assert allowed is False


@pytest.mark.parametrize(
    "tool_name",
    [
        "execute_shell",
        "run_terminal_command",
        "delete_files",
    ],
)

def test_blocked_tool(tool_name):

    policy = PolicyEngine()

    allowed, reason = policy.check_tool(
        tool_name,
        {},
    )

    assert allowed is False
    assert "explicitly blocked" in reason


def test_navigation_outside_boundaries():

    policy = PolicyEngine()

    allowed, reason = policy.check_tool(
        "navigate_to",
        {"x": 10.0, "y": 2.0},
    )

    assert allowed is False


def test_navigation_with_invalid_coordinates():

    policy = PolicyEngine()

    allowed, reason = policy.check_tool(
        "navigate_to",
        {"x": float("nan"), "y": 2.0},
    )

    assert allowed is False


def test_navigation_missing_arguments():

    policy = PolicyEngine()

    allowed, reason = policy.check_tool(
        "navigate_to",
        {"x": 2.0},
    )

    assert allowed is False


def test_navigation_with_extra_arguments():

    policy = PolicyEngine()

    allowed, reason = policy.check_tool(
        "navigate_to",
        {
            "x": 2.0,
            "y": 3.0,
            "execute_shell": True,
        },
    )

    assert allowed is False


def test_status_without_arguments():

    policy = PolicyEngine()

    allowed, reason = policy.check_tool(
        "get_robot_status",
        {},
    )

    assert allowed is True


def test_status_with_arguments():

    policy = PolicyEngine()

    allowed, reason = policy.check_tool(
        "get_robot_status",
        {"command": "delete"},
    )

    assert allowed is False

def test_navigation_boundary_coordinates():

    policy = PolicyEngine()

    allowed, reason = policy.check_tool(
        "navigate_to",
        {"x": -5.0, "y": 5.0},
    )

    assert allowed is True


@pytest.mark.parametrize(
    "coordinate",
    [float("inf"), float("-inf")],
)
def test_navigation_with_infinite_coordinates(coordinate):

    policy = PolicyEngine()

    allowed, reason = policy.check_tool(
        "navigate_to",
        {"x": coordinate, "y": 2.0},
    )

    assert allowed is False


def test_navigation_with_boolean_coordinates():

    policy = PolicyEngine()

    allowed, reason = policy.check_tool(
        "navigate_to",
        {"x": True, "y": 2.0},
    )

    assert allowed is False


def test_navigation_with_string_coordinates():

    policy = PolicyEngine()

    allowed, reason = policy.check_tool(
        "navigate_to",
        {"x": "1.0", "y": 2.0},
    )

    assert allowed is False


def test_get_coordinates_valid_position():

    policy = PolicyEngine()

    allowed, reason = policy.check_tool(
        "get_coordinates",
        {"position": [1.0, 2.0, 0.0]},
    )

    assert allowed is True


def test_get_coordinates_valid_tuple():

    policy = PolicyEngine()

    allowed, reason = policy.check_tool(
        "get_coordinates",
        {"position": (1.0, 2.0, 0.0)},
    )

    assert allowed is True


@pytest.mark.parametrize(
    "position",
    [
        [1.0, 2.0],
        [1.0, 2.0, 3.0, 4.0],
    ],
)
def test_get_coordinates_invalid_length(position):

    policy = PolicyEngine()

    allowed, reason = policy.check_tool(
        "get_coordinates",
        {"position": position},
    )

    assert allowed is False


def test_get_coordinates_with_nan():

    policy = PolicyEngine()

    allowed, reason = policy.check_tool(
        "get_coordinates",
        {"position": [float("nan"), 2.0, 0.0]},
    )

    assert allowed is False


def test_get_coordinates_with_infinity():

    policy = PolicyEngine()

    allowed, reason = policy.check_tool(
        "get_coordinates",
        {"position": [1.0, float("inf"), 0.0]},
    )

    assert allowed is False


def test_get_coordinates_with_boolean():

    policy = PolicyEngine()

    allowed, reason = policy.check_tool(
        "get_coordinates",
        {"position": [True, 2.0, 0.0]},
    )

    assert allowed is False


def test_get_coordinates_with_string():

    policy = PolicyEngine()

    allowed, reason = policy.check_tool(
        "get_coordinates",
        {"position": ["1.0", 2.0, 0.0]},
    )

    assert allowed is False


def test_get_coordinates_with_extra_arguments():

    policy = PolicyEngine()

    allowed, reason = policy.check_tool(
        "get_coordinates",
        {
            "position": [1.0, 2.0, 0.0],
            "command": "execute_shell",
        },
    )

    assert allowed is False


def test_get_coordinates_with_invalid_position_type():

    policy = PolicyEngine()

    allowed, reason = policy.check_tool(
        "get_coordinates",
        {"position": "1.0, 2.0, 0.0"},
    )

    assert allowed is False

def test_blocked_tool_cannot_be_allowlisted():

    policy = PolicyEngine()

    policy.allowed_tools.add("execute_shell")

    allowed, reason = policy.check_tool(
        "execute_shell",
        {},
    )

    assert allowed is False
    assert "explicitly blocked" in reason


if __name__ == "__main__":

    test_allowed_tool()
    test_unknown_tool()
    test_blocked_tool()
    test_navigation_outside_boundaries()
    test_navigation_with_invalid_coordinates()
    test_navigation_missing_arguments()
    test_navigation_with_extra_arguments()
    test_status_without_arguments()
    test_status_with_arguments()

    print("All policy tests passed!")
