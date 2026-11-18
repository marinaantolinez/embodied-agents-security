import rclpy

from rclpy.node import Node
from geometry_msgs.msg import PoseStamped

from security.goal_validator import GoalValidator


class GoalSecurityNode(Node):

    def __init__(self):
        super().__init__("goal_security_node")

        self.validator = GoalValidator(
            min_x=-5.0,
            max_x=5.0,
            min_y=-5.0,
            max_y=5.0,
            expected_frame="map",
        )

        self.subscription = self.create_subscription(
            PoseStamped,
            "/goal_point_candidate",
            self.goal_callback,
            10,
        )

        self.publisher = self.create_publisher(
            PoseStamped,
            "/goal_point",
            10,
        )

        self.get_logger().info(
            "Goal Security Node initialized"
        )

    def goal_callback(self, msg):

        accepted, reason = self.validator.validate(msg)

        if accepted:
            self.publisher.publish(msg)

            self.get_logger().info(
                f"Goal accepted: {reason}"
            )

        else:
            self.get_logger().warning(
                f"Goal rejected: {reason}"
            )


def main(args=None):

    rclpy.init(args=args)

    node = GoalSecurityNode()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
