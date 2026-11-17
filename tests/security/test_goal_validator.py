from types import SimpleNamespace

from security.goal_validator import GoalValidator


def create_goal(x=1.0, y=2.0, z=0.0, frame="map",
                qx=0.0, qy=0.0, qz=0.0, qw=1.0):

    return SimpleNamespace(
        header=SimpleNamespace(
            frame_id=frame
        ),
        pose=SimpleNamespace(
            position=SimpleNamespace(
                x=x,
                y=y,
                z=z,
            ),
            orientation=SimpleNamespace(
                x=qx,
                y=qy,
                z=qz,
                w=qw,
            ),
        ),
    )


def test_valid_goal():

    validator = GoalValidator()

    accepted, reason = validator.validate(create_goal())

    assert accepted is True


def test_goal_outside_boundaries():

    validator = GoalValidator()

    goal = create_goal(x=10.0)

    accepted, reason = validator.validate(goal)

    assert accepted is False


def test_goal_wrong_frame():

    validator = GoalValidator()

    goal = create_goal(frame="odom")

    accepted, reason = validator.validate(goal)

    assert accepted is False


def test_goal_with_nan():

    validator = GoalValidator()

    goal = create_goal(x=float("nan"))

    accepted, reason = validator.validate(goal)

    assert accepted is False


def test_goal_with_infinite_coordinate():

    validator = GoalValidator()

    goal = create_goal(y=float("inf"))

    accepted, reason = validator.validate(goal)

    assert accepted is False


def test_goal_with_invalid_quaternion():

    validator = GoalValidator()

    goal = create_goal(
        qx=0.0,
        qy=0.0,
        qz=0.0,
        qw=0.0,
    )

    accepted, reason = validator.validate(goal)

    assert accepted is False


def test_goal_with_non_normalized_quaternion():

    validator = GoalValidator()

    goal = create_goal(qw=2.0)

    accepted, reason = validator.validate(goal)

    assert accepted is False


def test_goal_with_invalid_structure():

    validator = GoalValidator()

    accepted, reason = validator.validate({})

    assert accepted is False


if __name__ == "__main__":

    test_valid_goal()
    test_goal_outside_boundaries()
    test_goal_wrong_frame()
    test_goal_with_nan()
    test_goal_with_infinite_coordinate()
    test_goal_with_invalid_quaternion()
    test_goal_with_non_normalized_quaternion()
    test_goal_with_invalid_structure()

    print("All goal validator tests passed!")
