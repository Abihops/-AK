#!/usr/bin/env python3
"""
VT LUNA Rover - Motion Capture Receiver Node

This node receives position data from the room's motion capture system
via WiFi and publishes it to ROS topics for navigation.

The motion capture cameras track the rover's position from above.
"""

import rospy
import socket
import json
import struct
from geometry_msgs.msg import PoseStamped, Pose, Point, Quaternion
from nav_msgs.msg import Odometry
from std_msgs.msg import Header

class MotionCaptureReceiver:
    def __init__(self):
        rospy.init_node('mocap_receiver', anonymous=False)
        
        # Parameters
        self.mocap_ip = rospy.get_param('~mocap_ip', '0.0.0.0')  # Listen on all interfaces
        self.mocap_port = rospy.get_param('~mocap_port', 5555)
        self.rover_id = rospy.get_param('~rover_id', 'rover_1')  # ID of your rover in mocap system
        self.protocol = rospy.get_param('~protocol', 'json')  # 'json' or 'binary'
        
        # Publishers
        self.pose_pub = rospy.Publisher('/mocap/pose', PoseStamped, queue_size=10)
        self.odom_pub = rospy.Publisher('/mocap/odom', Odometry, queue_size=10)
        
        # Setup UDP socket to receive mocap data
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.mocap_ip, self.mocap_port))
        self.sock.settimeout(1.0)  # 1 second timeout
        
        rospy.loginfo(f"Motion Capture Receiver Started")
        rospy.loginfo(f"Listening on {self.mocap_ip}:{self.mocap_port}")
        rospy.loginfo(f"Tracking rover ID: {self.rover_id}")
        
        # Start receiving data
        self.receive_loop()
    
    def receive_loop(self):
        """
        Main loop to receive and process motion capture data
        """
        rate = rospy.Rate(100)  # 100 Hz
        
        while not rospy.is_shutdown():
            try:
                # Receive data from motion capture system
                data, addr = self.sock.recvfrom(4096)
                
                # Parse based on protocol
                if self.protocol == 'json':
                    pose_data = self.parse_json(data)
                elif self.protocol == 'binary':
                    pose_data = self.parse_binary(data)
                else:
                    rospy.logwarn(f"Unknown protocol: {self.protocol}")
                    continue
                
                if pose_data:
                    self.publish_pose(pose_data)
                    
            except socket.timeout:
                # No data received, continue
                pass
            except Exception as e:
                rospy.logerr(f"Error receiving mocap data: {e}")
            
            rate.sleep()
    
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
            
            pose_data = {
                'position': msg.get('position', {}),
                'orientation': msg.get('orientation', {}),
                'timestamp': msg.get('timestamp', rospy.Time.now().to_sec())
            }
            
            return pose_data
            
        except json.JSONDecodeError as e:
            rospy.logwarn(f"Failed to parse JSON: {e}")
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
            
            pose_data = {
                'position': {'x': x, 'y': y, 'z': z},
                'orientation': {'x': qx, 'y': qy, 'z': qz, 'w': qw},
                'timestamp': rospy.Time.now().to_sec()
            }
            
            return pose_data
            
        except struct.error as e:
            rospy.logwarn(f"Failed to parse binary data: {e}")
            return None
    
    def publish_pose(self, pose_data):
        """
        Publish pose data to ROS topics
        """
        # Create PoseStamped message
        pose_msg = PoseStamped()
        pose_msg.header = Header()
        pose_msg.header.stamp = rospy.Time.now()
        pose_msg.header.frame_id = "mocap_world"
        
        # Position
        pose_msg.pose.position = Point(
            x=pose_data['position'].get('x', 0.0),
            y=pose_data['position'].get('y', 0.0),
            z=pose_data['position'].get('z', 0.0)
        )
        
        # Orientation (quaternion)
        pose_msg.pose.orientation = Quaternion(
            x=pose_data['orientation'].get('x', 0.0),
            y=pose_data['orientation'].get('y', 0.0),
            z=pose_data['orientation'].get('z', 0.0),
            w=pose_data['orientation'].get('w', 1.0)
        )
        
        # Publish PoseStamped
        self.pose_pub.publish(pose_msg)
        
        # Also publish as Odometry for navigation stack compatibility
        odom_msg = Odometry()
        odom_msg.header = pose_msg.header
        odom_msg.child_frame_id = "base_link"
        odom_msg.pose.pose = pose_msg.pose
        
        self.odom_pub.publish(odom_msg)
        
        rospy.logdebug(f"Published pose: x={pose_msg.pose.position.x:.2f}, "
                      f"y={pose_msg.pose.position.y:.2f}")
    
    def shutdown(self):
        """
        Cleanup on shutdown
        """
        self.sock.close()
        rospy.loginfo("Motion Capture Receiver Shutdown")

if __name__ == '__main__':
    try:
        receiver = MotionCaptureReceiver()
        rospy.on_shutdown(receiver.shutdown)
    except rospy.ROSInterruptException:
        pass
