#!/usr/bin/env python3
"""
VT LUNA Rover - Motion Capture Receiver Node

This node receives position data from the room's motion capture system
via WiFi and publishes it to ROS topics for navigation.

The motion capture cameras track the rover's position from above.
"""

import rclpy
from rclpy.node import Node
import socket
import json
import struct
from geometry_msgs.msg import PoseStamped, Pose, Point, Quaternion
from nav_msgs.msg import Odometry
from std_msgs.msg import Header


class MotionCaptureReceiver(Node):
    def __init__(self):
        super().__init__('mocap_receiver')

        # Parameters
        self.declare_parameter('mocap_ip', '0.0.0.0')
        self.declare_parameter('mocap_port', 5555)
        self.declare_parameter('rover_id', 'rover_1')
        self.declare_parameter('protocol', 'json')

        self.mocap_ip = self.get_parameter('mocap_ip').value
        self.mocap_port = self.get_parameter('mocap_port').value
        self.rover_id = self.get_parameter('rover_id').value
        self.protocol = self.get_parameter('protocol').value

        # Publishers
        self.pose_pub = self.create_publisher(PoseStamped, '/mocap/pose', 10)
        self.odom_pub = self.create_publisher(Odometry, '/mocap/odom', 10)

        # Setup UDP socket to receive mocap data
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.mocap_ip, self.mocap_port))
        self.sock.settimeout(0.01)  # Short timeout for non-blocking check

        self.get_logger().info(f"Motion Capture Receiver Started")
        self.get_logger().info(f"Listening on {self.mocap_ip}:{self.mocap_port}")
        self.get_logger().info(f"Tracking rover ID: {self.rover_id}")

        # Timer-based receive loop (100 Hz)
        self.timer = self.create_timer(0.01, self.receive_data)

    def receive_data(self):
        """
        Receive and process motion capture data (called by timer)
        """
        try:
            # Receive data from motion capture system
            data, addr = self.sock.recvfrom(4096)

            # Parse based on protocol
            if self.protocol == 'json':
                pose_data = self.parse_json(data)
            elif self.protocol == 'binary':
                pose_data = self.parse_binary(data)
            else:
                self.get_logger().warn(f"Unknown protocol: {self.protocol}")
                return

            if pose_data:
                self.publish_pose(pose_data)

        except socket.timeout:
            # No data received, continue
            pass
        except Exception as e:
            self.get_logger().error(f"Error receiving mocap data: {e}")

    def parse_json(self, data):
        """
        Parse JSON format motion capture data

        Expected format:
        {
            "id": "rover_1",
            "position": {"x": 1.5, "y": 2.3, "z": 0.0},
            "orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0},
            "timestamp": 1234567890.123
        }
        """
        try:
            msg = json.loads(data.decode('utf-8'))

            # Check if this data is for our rover
            if msg.get('id') != self.rover_id:
                return None

            now_sec = self.get_clock().now().nanoseconds / 1e9
            pose_data = {
                'position': msg.get('position', {}),
                'orientation': msg.get('orientation', {}),
                'timestamp': msg.get('timestamp', now_sec)
            }

            return pose_data

        except json.JSONDecodeError as e:
            self.get_logger().warn(f"Failed to parse JSON: {e}")
            return None

    def parse_binary(self, data):
        """
        Parse binary format motion capture data

        Expected format (32 bytes):
        - rover_id (4 bytes, int)
        - x, y, z position (12 bytes, 3 floats)
        - qx, qy, qz, qw orientation (16 bytes, 4 floats)
        """
        try:
            if len(data) < 32:
                return None

            # Unpack binary data
            # Format: i = int, f = float
            rover_id, x, y, z, qx, qy, qz, qw = struct.unpack('ifffffff', data[:32])

            # Check if this is our rover
            if rover_id != int(self.rover_id.split('_')[-1]):
                return None

            now_sec = self.get_clock().now().nanoseconds / 1e9
            pose_data = {
                'position': {'x': x, 'y': y, 'z': z},
                'orientation': {'x': qx, 'y': qy, 'z': qz, 'w': qw},
                'timestamp': now_sec
            }

            return pose_data

        except struct.error as e:
            self.get_logger().warn(f"Failed to parse binary data: {e}")
            return None

    def publish_pose(self, pose_data):
        """
        Publish pose data to ROS topics
        """
        now = self.get_clock().now().to_msg()

        # Create PoseStamped message
        pose_msg = PoseStamped()
        pose_msg.header.stamp = now
        pose_msg.header.frame_id = "mocap_world"

        # Position
        pose_msg.pose.position = Point(
            x=float(pose_data['position'].get('x', 0.0)),
            y=float(pose_data['position'].get('y', 0.0)),
            z=float(pose_data['position'].get('z', 0.0))
        )

        # Orientation (quaternion)
        pose_msg.pose.orientation = Quaternion(
            x=float(pose_data['orientation'].get('x', 0.0)),
            y=float(pose_data['orientation'].get('y', 0.0)),
            z=float(pose_data['orientation'].get('z', 0.0)),
            w=float(pose_data['orientation'].get('w', 1.0))
        )

        # Publish PoseStamped
        self.pose_pub.publish(pose_msg)

        # Also publish as Odometry for navigation stack compatibility
        odom_msg = Odometry()
        odom_msg.header = pose_msg.header
        odom_msg.child_frame_id = "base_link"
        odom_msg.pose.pose = pose_msg.pose

        self.odom_pub.publish(odom_msg)

        self.get_logger().debug(f"Published pose: x={pose_msg.pose.position.x:.2f}, "
                                f"y={pose_msg.pose.position.y:.2f}")

    def destroy_node(self):
        """
        Cleanup on shutdown
        """
        self.sock.close()
        self.get_logger().info("Motion Capture Receiver Shutdown")
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    receiver = MotionCaptureReceiver()
    try:
        rclpy.spin(receiver)
    except KeyboardInterrupt:
        pass
    finally:
        receiver.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
