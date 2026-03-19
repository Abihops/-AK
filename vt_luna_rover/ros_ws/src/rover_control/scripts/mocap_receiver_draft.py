#!/usr/bin/env python3
"""
VT LUNA Rover - Motion Capture Receiver Node (DRAFT)

This is a DRAFT script. After Wednesday's meeting with the mocap grad student,
update the connection settings based on what you learn.

This node connects to the motion capture system and publishes the rover's
position/orientation to ROS topics so the navigation controller can use it.

SUPPORTED PROTOCOLS (uncomment the one your lab uses):
  1. VRPN  - Most common (Vicon, OptiTrack, Qualisys all support this)
  2. NatNet - OptiTrack's native protocol
  3. UDP JSON - Simple custom UDP stream
  4. ROS Topic - If the lab already publishes to a ROS topic

AFTER WEDNESDAY'S MEETING, UPDATE THESE:
  - MOCAP_SERVER_IP: IP address of the mocap computer
  - MOCAP_PORT: port number
  - RIGID_BODY_NAME: whatever name they give your rover in the mocap software
  - PROTOCOL: which protocol the system uses
"""

import rospy
import math
import time
import socket
import json
import struct
from geometry_msgs.msg import PoseStamped, Twist, Point, Quaternion, TransformStamped
from nav_msgs.msg import Odometry
from std_msgs.msg import Header, Bool


# ============================================================
# CONFIGURATION - UPDATE AFTER WEDNESDAY'S MEETING
# ============================================================
MOCAP_SERVER_IP = "192.168.1.100"   # this could vary depending on the mocap system
MOCAP_PORT = 3883                    # <-- VRPN default is 3883
RIGID_BODY_NAME = "rover_1"         # <-- Name of your rover in mocap software
PROTOCOL = "vrpn"                    # <-- Options: "vrpn", "natnet", "udp_json", "ros_topic"
# ============================================================


class MocapReceiverDraft:
    def __init__(self):
        rospy.init_node('mocap_receiver', anonymous=False)

        # ---- ROS Parameters (can override from launch file) ----
        self.server_ip = rospy.get_param('~mocap_ip', MOCAP_SERVER_IP)
        self.port = rospy.get_param('~mocap_port', MOCAP_PORT)
        self.body_name = rospy.get_param('~rigid_body_name', RIGID_BODY_NAME)
        self.protocol = rospy.get_param('~protocol', PROTOCOL)

        # ---- Publishers ----
        # Main pose output - navigation_controller.py subscribes to this
        self.pose_pub = rospy.Publisher('/mocap/pose', PoseStamped, queue_size=10)

        # Odometry output - compatible with ROS navigation stack
        self.odom_pub = rospy.Publisher('/mocap/odom', Odometry, queue_size=10)

        # Status - so other nodes know if mocap is working
        self.status_pub = rospy.Publisher('/mocap/connected', Bool, queue_size=10)

        # ---- Tracking State ----
        self.last_pose_time = None
        self.pose_count = 0
        self.connected = False

        # ---- Previous pose for velocity calculation ----
        self.prev_position = None
        self.prev_time = None

        rospy.loginfo("=" * 50)
        rospy.loginfo("Motion Capture Receiver (DRAFT)")
        rospy.loginfo(f"  Server: {self.server_ip}:{self.port}")
        rospy.loginfo(f"  Rigid Body: {self.body_name}")
        rospy.loginfo(f"  Protocol: {self.protocol}")
        rospy.loginfo("=" * 50)

        # ---- Start the right receiver based on protocol ----
        if self.protocol == "vrpn":
            self.run_vrpn()
        elif self.protocol == "natnet":
            self.run_natnet()
        elif self.protocol == "udp_json":
            self.run_udp_json()
        elif self.protocol == "ros_topic":
            self.run_ros_relay()
        else:
            rospy.logerr(f"Unknown protocol: {self.protocol}")
            rospy.logerr("Options: vrpn, natnet, udp_json, ros_topic")

    # ============================================================
    # OPTION 1: VRPN (Most Common)
    # ============================================================
    # Install: sudo apt install ros-noetic-vrpn-client-ros
    # Or: pip3 install vrpn
    #
    # This is the most likely protocol your lab uses.
    # VRPN works with Vicon, OptiTrack, and Qualisys systems.
    # ============================================================
    def run_vrpn(self):
        """
        Connect to mocap via VRPN protocol.

        If the lab has ros-noetic-vrpn-client-ros installed, you can
        skip this script and just run:
            roslaunch vrpn_client_ros sample.launch server:=192.168.1.100

        That will automatically publish to /vrpn_client_node/<body_name>/pose
        """
        try:
            # Try importing vrpn python bindings
            import vrpn
            rospy.loginfo("Using python-vrpn library")
            self._run_vrpn_python(vrpn)
        except ImportError:
            rospy.logwarn("python-vrpn not installed. Trying vrpn_client_ros relay...")
            rospy.logwarn("Install with: pip3 install vrpn")
            rospy.logwarn("")
            rospy.logwarn("ALTERNATIVE: Run this command in another terminal:")
            rospy.logwarn(f"  roslaunch vrpn_client_ros sample.launch server:={self.server_ip}")
            rospy.logwarn(f"  Then set protocol to 'ros_topic' and topic to '/vrpn_client_node/{self.body_name}/pose'")

            # Fall back to subscribing to vrpn_client_ros topic
            topic = f"/vrpn_client_node/{self.body_name}/pose"
            rospy.loginfo(f"Subscribing to: {topic}")
            rospy.Subscriber(topic, PoseStamped, self._vrpn_ros_callback)
            rospy.spin()

    def _run_vrpn_python(self, vrpn):
        """Use the python vrpn library directly"""
        tracker = vrpn.receiver.Tracker(f"{self.body_name}@{self.server_ip}:{self.port}")
        tracker.register_change_handler("position", self._vrpn_position_callback, "tracker")

        rate = rospy.Rate(100)  # 100 Hz
        while not rospy.is_shutdown():
            tracker.mainloop()
            self._check_connection_status()
            rate.sleep()

    def _vrpn_position_callback(self, userdata, data):
        """Callback when VRPN receives new position data"""
        pos = data['position']
        quat = data['quaternion']

        pose_data = {
            'position': {'x': pos[0], 'y': pos[1], 'z': pos[2]},
            'orientation': {'x': quat[0], 'y': quat[1], 'z': quat[2], 'w': quat[3]}
        }
        self.publish_pose(pose_data)

    def _vrpn_ros_callback(self, msg):
        """Relay from vrpn_client_ros topic"""
        pose_data = {
            'position': {
                'x': msg.pose.position.x,
                'y': msg.pose.position.y,
                'z': msg.pose.position.z
            },
            'orientation': {
                'x': msg.pose.orientation.x,
                'y': msg.pose.orientation.y,
                'z': msg.pose.orientation.z,
                'w': msg.pose.orientation.w
            }
        }
        self.publish_pose(pose_data)

    # ============================================================
    # OPTION 2: NatNet (OptiTrack only)
    # ============================================================
    # Install: pip3 install natnet-client
    # OptiTrack's native protocol - higher performance than VRPN
    # ============================================================
    def run_natnet(self):
        """Connect to OptiTrack Motive via NatNet SDK"""
        try:
            from natnet import NatNetClient
        except ImportError:
            rospy.logerr("natnet-client not installed!")
            rospy.logerr("Install with: pip3 install natnet-client")
            return

        client = NatNetClient()
        client.set_server_address(self.server_ip)
        client.rigid_body_listener = self._natnet_rigid_body_callback
        
        rospy.loginfo("Connecting to OptiTrack Motive...")
        client.run()

        rospy.spin()

    def _natnet_rigid_body_callback(self, rigid_body_id, position, rotation):
        """Callback for NatNet rigid body data"""
        pose_data = {
            'position': {'x': position[0], 'y': position[1], 'z': position[2]},
            'orientation': {'x': rotation[0], 'y': rotation[1], 'z': rotation[2], 'w': rotation[3]}
        }
        self.publish_pose(pose_data)

    # ============================================================
    # OPTION 3: UDP JSON (Simple custom stream)
    # ============================================================
    # If the grad student has a custom script that streams data
    # over UDP, this is the simplest approach.
    # ============================================================
    def run_udp_json(self):
        """Receive mocap data as JSON over UDP"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', self.port))
        sock.settimeout(1.0)

        rospy.loginfo(f"Listening for UDP JSON on port {self.port}")

        rate = rospy.Rate(100)
        while not rospy.is_shutdown():
            try:
                data, addr = sock.recvfrom(4096)
                msg = json.loads(data.decode('utf-8'))

                # Filter for our rover
                if msg.get('id') == self.body_name or msg.get('name') == self.body_name:
                    pos = msg.get('position', msg.get('pos', {}))
                    rot = msg.get('orientation', msg.get('quat', {}))

                    pose_data = {
                        'position': {
                            'x': pos.get('x', pos[0] if isinstance(pos, list) else 0),
                            'y': pos.get('y', pos[1] if isinstance(pos, list) else 0),
                            'z': pos.get('z', pos[2] if isinstance(pos, list) else 0),
                        },
                        'orientation': {
                            'x': rot.get('x', rot[0] if isinstance(rot, list) else 0),
                            'y': rot.get('y', rot[1] if isinstance(rot, list) else 0),
                            'z': rot.get('z', rot[2] if isinstance(rot, list) else 0),
                            'w': rot.get('w', rot[3] if isinstance(rot, list) else 1),
                        }
                    }
                    self.publish_pose(pose_data)

            except socket.timeout:
                pass
            except Exception as e:
                rospy.logwarn(f"UDP parse error: {e}")

            self._check_connection_status()
            rate.sleep()

        sock.close()

    # ============================================================
    # OPTION 4: ROS Topic Relay
    # ============================================================
    # If the lab computer already publishes pose data to a ROS topic,
    # we just relay it to our standard topic names.
    # ============================================================
    def run_ros_relay(self):
        """Subscribe to an existing ROS topic from the mocap system"""
        # Common topic names from different mocap ROS packages
        possible_topics = [
            f"/vrpn_client_node/{self.body_name}/pose",   # vrpn_client_ros
            f"/mocap_node/{self.body_name}/pose",          # mocap_optitrack
            f"/qualisys/{self.body_name}/pose",            # qualisys_driver
            f"/vicon/{self.body_name}/{self.body_name}",   # vicon_bridge
        ]

        # Try to find which topic is active
        source_topic = rospy.get_param('~source_topic', possible_topics[0])
        rospy.loginfo(f"Relaying from: {source_topic}")
        rospy.loginfo(f"Publishing to: /mocap/pose")

        rospy.Subscriber(source_topic, PoseStamped, self._vrpn_ros_callback)
        rospy.spin()

    # ============================================================
    # SHARED: Publish pose to standard ROS topics
    # ============================================================
    def publish_pose(self, pose_data):
        """
        Publish pose data to /mocap/pose (PoseStamped) and /mocap/odom (Odometry).
        These are the topics that navigation_controller.py subscribes to.
        """
        now = rospy.Time.now()

        # --- PoseStamped ---
        pose_msg = PoseStamped()
        pose_msg.header.stamp = now
        pose_msg.header.frame_id = "mocap_world"

        pose_msg.pose.position = Point(
            x=pose_data['position']['x'],
            y=pose_data['position']['y'],
            z=pose_data['position']['z']
        )
        pose_msg.pose.orientation = Quaternion(
            x=pose_data['orientation']['x'],
            y=pose_data['orientation']['y'],
            z=pose_data['orientation']['z'],
            w=pose_data['orientation']['w']
        )

        self.pose_pub.publish(pose_msg)

        # --- Odometry (with velocity estimate) ---
        odom_msg = Odometry()
        odom_msg.header.stamp = now
        odom_msg.header.frame_id = "mocap_world"
        odom_msg.child_frame_id = "base_link"
        odom_msg.pose.pose = pose_msg.pose

        # Estimate velocity from consecutive poses
        curr_pos = pose_data['position']
        curr_time = now.to_sec()

        if self.prev_position is not None and self.prev_time is not None:
            dt = curr_time - self.prev_time
            if dt > 0:
                odom_msg.twist.twist.linear.x = (curr_pos['x'] - self.prev_position['x']) / dt
                odom_msg.twist.twist.linear.y = (curr_pos['y'] - self.prev_position['y']) / dt
                odom_msg.twist.twist.linear.z = (curr_pos['z'] - self.prev_position['z']) / dt

        self.prev_position = curr_pos
        self.prev_time = curr_time

        self.odom_pub.publish(odom_msg)

        # --- Update tracking ---
        self.last_pose_time = now
        self.pose_count += 1
        self.connected = True

        if self.pose_count % 100 == 0:
            rospy.loginfo(f"Mocap OK | Poses received: {self.pose_count} | "
                         f"Pos: ({curr_pos['x']:.2f}, {curr_pos['y']:.2f}, {curr_pos['z']:.2f})")

    def _check_connection_status(self):
        """Check if we're still receiving data"""
        if self.last_pose_time is not None:
            time_since = (rospy.Time.now() - self.last_pose_time).to_sec()
            if time_since > 2.0:
                if self.connected:
                    rospy.logwarn("Lost connection to motion capture system!")
                    self.connected = False
                self.status_pub.publish(Bool(data=False))
            else:
                self.status_pub.publish(Bool(data=True))

    def shutdown(self):
        """Cleanup on shutdown"""
        rospy.loginfo("Motion Capture Receiver shutting down")


if __name__ == '__main__':
    try:
        receiver = MocapReceiverDraft()
        rospy.on_shutdown(receiver.shutdown)
    except rospy.ROSInterruptException:
        pass
