#!/usr/bin/env python3
"""
VT LUNA Rover - Vision Processing Node

This node processes camera images for object detection and tracking.
Implements sample manipulation using visual feedback.
"""

import rospy
import cv2
import numpy as np
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist, Point
from std_msgs.msg import Int16MultiArray, Bool
from cv_bridge import CvBridge, CvBridgeError

class VisionNode:
    def __init__(self):
        rospy.init_node('vision_node', anonymous=False)
        
        # Parameters
        self.target_color_lower = rospy.get_param('~target_color_lower', [0, 100, 100])
        self.target_color_upper = rospy.get_param('~target_color_upper', [10, 255, 255])
        self.min_area = rospy.get_param('~min_area', 500)
        
        # CV Bridge
        self.bridge = CvBridge()
        
        # State variables
        self.current_frame = None
        self.target_detected = False
        self.target_center = Point()
        
        # Subscribers
        self.image_sub = rospy.Subscriber('/camera/image_raw', Image, self.image_callback)
        
        # Publishers
        self.processed_image_pub = rospy.Publisher('/camera/image_processed', Image, queue_size=10)
        self.target_pub = rospy.Publisher('/target_position', Point, queue_size=10)
        self.detection_pub = rospy.Publisher('/target_detected', Bool, queue_size=10)
        self.servo_cmd_pub = rospy.Publisher('/servo_cmd', Int16MultiArray, queue_size=10)
        
        rospy.loginfo("Vision Node Started")
    
    def image_callback(self, msg):
        """
        Process incoming camera images
        """
        try:
            # Convert ROS Image to OpenCV format
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            self.current_frame = cv_image
            
            # Process image for object detection
            self.detect_target(cv_image)
            
        except CvBridgeError as e:
            rospy.logerr(f"CV Bridge Error: {e}")
    
    def detect_target(self, frame):
        """
        Detect target object using color-based detection
        """
        # Convert to HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Create mask for target color
        lower = np.array(self.target_color_lower)
        upper = np.array(self.target_color_upper)
        mask = cv2.inRange(hsv, lower, upper)
        
        # Morphological operations to reduce noise
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=2)
        mask = cv2.dilate(mask, kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Process contours
        if contours:
            # Find largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest_contour)
            
            if area > self.min_area:
                # Calculate centroid
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    
                    # Update target position
                    self.target_center.x = cx
                    self.target_center.y = cy
                    self.target_center.z = area
                    self.target_detected = True
                    
                    # Draw on frame
                    cv2.drawContours(frame, [largest_contour], -1, (0, 255, 0), 2)
                    cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                    cv2.putText(frame, f"Target: ({cx}, {cy})", (cx + 10, cy - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    
                    # Publish target position
                    self.target_pub.publish(self.target_center)
                    self.detection_pub.publish(Bool(data=True))
                    
                    # Track target with servo
                    self.track_target(cx, cy, frame.shape[1], frame.shape[0])
                else:
                    self.target_detected = False
                    self.detection_pub.publish(Bool(data=False))
            else:
                self.target_detected = False
                self.detection_pub.publish(Bool(data=False))
        else:
            self.target_detected = False
            self.detection_pub.publish(Bool(data=False))
        
        # Publish processed image
        try:
            processed_msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
            processed_msg.header.stamp = rospy.Time.now()
            self.processed_image_pub.publish(processed_msg)
        except CvBridgeError as e:
            rospy.logerr(f"CV Bridge Error: {e}")
    
    def track_target(self, target_x, target_y, frame_width, frame_height):
        """
        Calculate servo angles to center target in frame
        """
        # Calculate error from center
        center_x = frame_width / 2
        center_y = frame_height / 2
        
        error_x = target_x - center_x
        error_y = target_y - center_y
        
        # Simple proportional control
        # Adjust gains based on your servo response
        kp_x = 0.1
        kp_y = 0.1
        
        # Current servo positions (you might want to track these)
        current_pan = 90
        current_tilt = 90
        
        # Calculate new servo positions
        new_pan = int(current_pan - (error_x * kp_x))
        new_tilt = int(current_tilt + (error_y * kp_y))
        
        # Constrain to valid range
        new_pan = max(0, min(180, new_pan))
        new_tilt = max(0, min(180, new_tilt))
        
        # Publish servo command
        servo_msg = Int16MultiArray()
        servo_msg.data = [new_pan, new_tilt]
        self.servo_cmd_pub.publish(servo_msg)

if __name__ == '__main__':
    try:
        node = VisionNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
