#!/usr/bin/env python3
"""
VT LUNA Rover - Autonomous Control Node

This node implements autonomous behavior for sample manipulation
using visual feedback from the camera.
"""

import rospy
from geometry_msgs.msg import Twist, Point
from std_msgs.msg import Bool, String
import math

class AutonomousControl:
    def __init__(self):
        rospy.init_node('autonomous_control', anonymous=False)
        
        # Parameters
        self.max_linear_speed = rospy.get_param('~max_linear_speed', 0.3)  # m/s
        self.max_angular_speed = rospy.get_param('~max_angular_speed', 1.0)  # rad/s
        self.target_distance_threshold = rospy.get_param('~target_distance', 1000)  # pixels
        
        # State variables
        self.target_position = Point()
        self.target_detected = False
        self.autonomous_mode = False
        self.state = "SEARCHING"  # SEARCHING, APPROACHING, MANIPULATING, DONE
        
        # Subscribers
        self.target_sub = rospy.Subscriber('/target_position', Point, self.target_callback)
        self.detection_sub = rospy.Subscriber('/target_detected', Bool, self.detection_callback)
        self.mode_sub = rospy.Subscriber('/autonomous_mode', Bool, self.mode_callback)
        
        # Publishers
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        self.state_pub = rospy.Publisher('/rover_state', String, queue_size=10)
        
        # Control loop timer
        self.control_timer = rospy.Timer(rospy.Duration(0.1), self.control_loop)
        
        rospy.loginfo("Autonomous Control Node Started")
    
    def target_callback(self, msg):
        """Update target position"""
        self.target_position = msg
    
    def detection_callback(self, msg):
        """Update target detection status"""
        self.target_detected = msg.data
    
    def mode_callback(self, msg):
        """Enable/disable autonomous mode"""
        self.autonomous_mode = msg.data
        if self.autonomous_mode:
            rospy.loginfo("Autonomous mode ENABLED")
            self.state = "SEARCHING"
        else:
            rospy.loginfo("Autonomous mode DISABLED")
            self.stop_rover()
    
    def control_loop(self, event):
        """Main control loop"""
        if not self.autonomous_mode:
            return
        
        # State machine
        if self.state == "SEARCHING":
            self.search_behavior()
        elif self.state == "APPROACHING":
            self.approach_behavior()
        elif self.state == "MANIPULATING":
            self.manipulate_behavior()
        elif self.state == "DONE":
            self.stop_rover()
        
        # Publish current state
        self.state_pub.publish(String(data=self.state))
    
    def search_behavior(self):
        """
        Rotate in place to search for target
        """
        if self.target_detected:
            rospy.loginfo("Target detected! Switching to APPROACHING")
            self.state = "APPROACHING"
            return
        
        # Rotate slowly
        cmd = Twist()
        cmd.angular.z = 0.3  # Slow rotation
        self.cmd_vel_pub.publish(cmd)
    
    def approach_behavior(self):
        """
        Approach the detected target
        """
        if not self.target_detected:
            rospy.logwarn("Target lost! Returning to SEARCHING")
            self.state = "SEARCHING"
            return
        
        # Get target position in image (assuming 640x480 image)
        image_center_x = 320
        target_x = self.target_position.x
        target_area = self.target_position.z
        
        # Calculate error
        error_x = target_x - image_center_x
        
        # Proportional control
        kp_angular = 0.003
        kp_linear = 0.0005
        
        cmd = Twist()
        
        # Angular velocity to center target
        cmd.angular.z = -error_x * kp_angular
        cmd.angular.z = max(min(cmd.angular.z, self.max_angular_speed), -self.max_angular_speed)
        
        # Linear velocity based on distance (area)
        if target_area < self.target_distance_threshold:
            # Move forward if target is far
            cmd.linear.x = self.max_linear_speed * 0.5
        else:
            # Close enough, switch to manipulation
            rospy.loginfo("Target reached! Switching to MANIPULATING")
            self.state = "MANIPULATING"
            cmd.linear.x = 0
        
        self.cmd_vel_pub.publish(cmd)
    
    def manipulate_behavior(self):
        """
        Perform sample manipulation
        """
        # Stop the rover
        self.stop_rover()
        
        # In a real implementation, you would:
        # 1. Activate manipulator/gripper
        # 2. Perform sample collection
        # 3. Store sample
        
        rospy.loginfo("Performing sample manipulation...")
        rospy.sleep(3)  # Simulate manipulation time
        
        rospy.loginfo("Manipulation complete!")
        self.state = "DONE"
    
    def stop_rover(self):
        """Stop all rover motion"""
        cmd = Twist()
        cmd.linear.x = 0
        cmd.angular.z = 0
        self.cmd_vel_pub.publish(cmd)

if __name__ == '__main__':
    try:
        controller = AutonomousControl()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
