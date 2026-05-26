#!/usr/bin/env python3

# VT LUNA Rover - Hardware Test Node
# Runs a step-by-step test of every motor and servo
# Use this to verify wiring and direction before full testing
#
# Run alongside motor_bridge.py:
#   Terminal 1: ros2 run rover_control motor_bridge.py
#   Terminal 2: ros2 run rover_control hardware_test.py
#
# It will walk through each motor and servo with a pause in between
# so you can see if everything spins in the right direction

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time


TEST_SPEED    = 0.25   # slow speed for safety during testing (m/s)
TEST_DURATION = 1.5    # how long each test runs in seconds
PAUSE         = 1.0    # pause between tests in seconds


class HardwareTest(Node):
    def __init__(self):
        super().__init__('hardware_test')

        self.cmd_vel_pub = self.create_publisher(Twist,             '/cmd_vel',         10)

        # Wait a moment for motor_bridge to be ready
        self.get_logger().info("Hardware test starting in 2 seconds...")
        time.sleep(2.0)

        self.run_tests()

    def run_tests(self):
        self.get_logger().info("=== VT LUNA Rover Hardware Test ===")

        # Test 1: Drive forward (both sides forward)
        self.log_test("TEST 1: Drive forward - all 4 wheel motors")
        self.send_drive(TEST_SPEED, 0.0)
        time.sleep(TEST_DURATION)
        self.stop()
        time.sleep(PAUSE)

        # Test 2: Drive backward
        self.log_test("TEST 2: Drive backward")
        self.send_drive(-TEST_SPEED, 0.0)
        time.sleep(TEST_DURATION)
        self.stop()
        time.sleep(PAUSE)

        # Test 3: Spin left (left wheels back, right wheels forward)
        self.log_test("TEST 3: Spin left in place")
        self.send_drive(0.0, TEST_SPEED * 2)
        time.sleep(TEST_DURATION)
        self.stop()
        time.sleep(PAUSE)

        # Test 4: Spin right
        self.log_test("TEST 4: Spin right in place")
        self.send_drive(0.0, -TEST_SPEED * 2)
        time.sleep(TEST_DURATION)
        self.stop()
        time.sleep(PAUSE)

        self.get_logger().info("=== Hardware test complete ===")
        self.get_logger().info("Check that all wheel motors spun correctly")
        self.get_logger().info("If a motor spun backwards, flip the DIR wire on that Cytron driver")

    def send_drive(self, linear, angular):
        twist = Twist()
        twist.linear.x  = linear
        twist.angular.z = angular
        self.cmd_vel_pub.publish(twist)

    def stop(self):
        self.cmd_vel_pub.publish(Twist())

    def log_test(self, msg):
        self.get_logger().info(f"\n--- {msg} ---")


def main(args=None):
    rclpy.init(args=args)
    node = HardwareTest()
    rclpy.spin_once(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
