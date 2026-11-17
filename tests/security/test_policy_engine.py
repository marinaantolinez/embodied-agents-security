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


def test_blocked_tool():

    policy = PolicyEngine()

    allowed, reason = policy.check_tool(
        "execute_shell",
        {},
    )

    assert allowed is False


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
