#!/usr/bin/env python3

# VT LUNA Rover - Keyboard Teleop
# Drive the rover with keyboard keys, no mocap needed
# Run this alongside motor_bridge.py to control the rover manually
#
# Controls:
#   W / S      forward / backward
#   A / D      turn left / turn right
#   Q / E      strafe turn (spin in place)
#   space      stop
#   T / G      mechanism motor forward / reverse
#   1 / 2 / 3  center servo 1 / 2 / 3
#   Ctrl+C     quit

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32, Float32MultiArray
import sys
import tty
import termios
import threading


# Speed settings - tweak these to your comfort
LINEAR_SPEED  = 0.4   # m/s forward/backward
ANGULAR_SPEED = 0.8   # rad/s turning
MECH_SPEED    = 0.5   # mechanism motor (0.0 to 1.0)


class TeleopKeyboard(Node):
    def __init__(self):
        super().__init__('teleop_keyboard')

        self.cmd_vel_pub  = self.create_publisher(Twist,             '/cmd_vel',         10)
        self.mech_pub     = self.create_publisher(Float32,           '/mechanism/speed', 10)
        self.servo_pub    = self.create_publisher(Float32MultiArray, '/servo/angles',    10)

        # Current servo angles - start centered
        self.servo_angles = [90.0, 90.0, 90.0]

        self.get_logger().info("Teleop keyboard ready")
        self.get_logger().info("W/S=drive  A/D=turn  Q/E=spin  SPACE=stop  T/G=mech  1/2/3=servos  Ctrl+C=quit")

        # Run the key reading loop in a background thread
        self.running = True
        thread = threading.Thread(target=self.key_loop, daemon=True)
        thread.start()

    def key_loop(self):
        # Set terminal to raw mode so we get keypresses instantly without enter
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while self.running:
                key = sys.stdin.read(1)
                self.handle_key(key)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def handle_key(self, key):
        twist = Twist()

        if key == 'w':
            twist.linear.x = LINEAR_SPEED
        elif key == 's':
            twist.linear.x = -LINEAR_SPEED
        elif key == 'a':
            twist.angular.z = ANGULAR_SPEED
        elif key == 'd':
            twist.angular.z = -ANGULAR_SPEED
        elif key == 'q':
            # Spin left in place
            twist.angular.z = ANGULAR_SPEED
        elif key == 'e':
            # Spin right in place
            twist.angular.z = -ANGULAR_SPEED
        elif key == ' ':
            # Stop everything
            twist = Twist()
        elif key == 't':
            self.mech_pub.publish(Float32(data=MECH_SPEED))
            return
        elif key == 'g':
            self.mech_pub.publish(Float32(data=-MECH_SPEED))
            return
        elif key == '1':
            self.servo_angles[0] = 90.0
            self.publish_servos()
            return
        elif key == '2':
            self.servo_angles[1] = 90.0
            self.publish_servos()
            return
        elif key == '3':
            self.servo_angles[2] = 90.0
            self.publish_servos()
            return
        elif key == '\x03':
            # Ctrl+C - stop and quit
            self.cmd_vel_pub.publish(Twist())
            self.running = False
            return
        else:
            return

        self.cmd_vel_pub.publish(twist)

    def publish_servos(self):
        msg = Float32MultiArray()
        msg.data = self.servo_angles
        self.servo_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = TeleopKeyboard()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.cmd_vel_pub.publish(Twist())  # stop on exit
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
