#!/usr/bin/env python3
"""
VT LUNA Rover - Navigation Controller

This node uses position data from the motion capture system
to navigate the rover to target locations for sample manipulation.
"""

import rclpy
from rclpy.node import Node
import math
from geometry_msgs.msg import PoseStamped, Twist, Point
from std_msgs.msg import Bool, String
from nav_msgs.msg import Odometry


class NavigationController(Node):
    def __init__(self):
        super().__init__('navigation_controller')

        # Parameters
        self.declare_parameter('max_linear_speed', 0.3)
        self.declare_parameter('max_angular_speed', 1.0)
        self.declare_parameter('position_tolerance', 0.1)
        self.declare_parameter('angle_tolerance', 0.1)

        self.max_linear_speed = self.get_parameter('max_linear_speed').value
        self.max_angular_speed = self.get_parameter('max_angular_speed').value
        self.position_tolerance = self.get_parameter('position_tolerance').value
        self.angle_tolerance = self.get_parameter('angle_tolerance').value

        # State variables
        self.current_pose = None
        self.target_position = None
        self.navigation_enabled = False
        self.state = "IDLE"  # IDLE, ROTATING, MOVING, REACHED

        # Subscribers
        self.pose_sub = self.create_subscription(PoseStamped, '/mocap/pose', self.pose_callback, 10)
        self.target_sub = self.create_subscription(Point, '/target_location', self.target_callback, 10)
        self.nav_enable_sub = self.create_subscription(Bool, '/navigation_enabled', self.nav_enable_callback, 10)

        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.state_pub = self.create_publisher(String, '/nav_state', 10)
        self.reached_pub = self.create_publisher(Bool, '/target_reached', 10)

        # Control loop (20 Hz)
        self.control_timer = self.create_timer(0.05, self.control_loop)

        self.get_logger().info("Navigation Controller Started")

    def pose_callback(self, msg):
        """Update current pose from motion capture"""
        self.current_pose = msg.pose

    def target_callback(self, msg):
        """Set new target position"""
        self.target_position = msg
        self.state = "ROTATING"
        self.get_logger().info(f"New target: x={msg.x:.2f}, y={msg.y:.2f}")

    def nav_enable_callback(self, msg):
        """Enable/disable navigation"""
        self.navigation_enabled = msg.data
        if not self.navigation_enabled:
            self.stop_rover()
            self.state = "IDLE"

    def control_loop(self):
        """Main navigation control loop"""
        if not self.navigation_enabled or self.current_pose is None:
            return

        if self.target_position is None:
            self.stop_rover()
            return

        # Calculate distance and angle to target
        dx = self.target_position.x - self.current_pose.position.x
        dy = self.target_position.y - self.current_pose.position.y
        distance = math.sqrt(dx**2 + dy**2)
        target_angle = math.atan2(dy, dx)

        # Get current heading from quaternion
        current_heading = self.quaternion_to_yaw(self.current_pose.orientation)

        # Calculate angle error
        angle_error = self.normalize_angle(target_angle - current_heading)

        # State machine for navigation
        if self.state == "ROTATING":
            self.rotate_to_target(angle_error)

        elif self.state == "MOVING":
            self.move_to_target(distance, angle_error)

        elif self.state == "REACHED":
            self.stop_rover()
            self.reached_pub.publish(Bool(data=True))

        # Publish state
        self.state_pub.publish(String(data=self.state))

    def rotate_to_target(self, angle_error):
        """Rotate to face the target"""
        if abs(angle_error) < self.angle_tolerance:
            # Aligned with target, start moving
            self.state = "MOVING"
            self.get_logger().info("Aligned with target, moving forward")
            return

        # Proportional control for rotation
        cmd = Twist()
        kp_angular = 1.0
        cmd.angular.z = kp_angular * angle_error
        cmd.angular.z = max(min(cmd.angular.z, self.max_angular_speed), -self.max_angular_speed)

        self.cmd_vel_pub.publish(cmd)

    def move_to_target(self, distance, angle_error):
        """Move toward the target while maintaining heading"""
        if distance < self.position_tolerance:
            # Reached target
            self.state = "REACHED"
            self.get_logger().info("Target reached!")
            return

        # If heading error is too large, go back to rotating
        if abs(angle_error) > self.angle_tolerance * 3:
            self.state = "ROTATING"
            self.get_logger().info("Lost heading, re-aligning")
            return

        # Proportional control
        cmd = Twist()
        kp_linear = 0.5
        kp_angular = 0.5

        # Linear velocity based on distance
        cmd.linear.x = kp_linear * distance
        cmd.linear.x = max(min(cmd.linear.x, self.max_linear_speed), 0.0)

        # Small angular correction to maintain heading
        cmd.angular.z = kp_angular * angle_error
        cmd.angular.z = max(min(cmd.angular.z, self.max_angular_speed), -self.max_angular_speed)

        self.cmd_vel_pub.publish(cmd)

    def quaternion_to_yaw(self, q):
        """
        Convert quaternion to yaw angle (rotation around z-axis)
        """
        # Yaw (z-axis rotation)
        siny_cosp = 2 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z)
        yaw = math.atan2(siny_cosp, cosy_cosp)
        return yaw

    def normalize_angle(self, angle):
        """Normalize angle to [-pi, pi]"""
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle

    def stop_rover(self):
        """Stop all rover motion"""
        cmd = Twist()
        self.cmd_vel_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    controller = NavigationController()
    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        pass
    finally:
        controller.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
