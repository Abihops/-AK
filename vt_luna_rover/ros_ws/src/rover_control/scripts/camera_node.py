#!/usr/bin/env python3
"""
VT LUNA Rover - Camera Node

This node captures camera images and publishes them to ROS topics
for processing by vision nodes.
"""

import rospy
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

class CameraNode:
    def __init__(self): 
        rospy.init_node('camera_node', anonymous=False)
        
        # Parameters
        self.camera_id = rospy.get_param('~camera_id', 0)
        self.frame_rate = rospy.get_param('~frame_rate', 30)
        self.image_width = rospy.get_param('~image_width', 640)
        self.image_height = rospy.get_param('~image_height', 480)
        
        # Initialize camera
        self.cap = cv2.VideoCapture(self.camera_id)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.image_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.image_height)
        self.cap.set(cv2.CAP_PROP_FPS, self.frame_rate)
        
        if not self.cap.isOpened():
            rospy.logerr("Failed to open camera")
            return
        
        # CV Bridge for converting between OpenCV and ROS images
        self.bridge = CvBridge()
        
        # Publishers
        self.image_pub = rospy.Publisher('/camera/image_raw', Image, queue_size=10)
        
        # Timer for capturing frames
        self.timer = rospy.Timer(rospy.Duration(1.0/self.frame_rate), self.capture_frame)
        
        rospy.loginfo(f"Camera Node Started - Camera {self.camera_id}")
    
    def capture_frame(self, event):
        """
        Capture and publish camera frame
        """
        ret, frame = self.cap.read()
        
        if ret:
            try:
                # Convert OpenCV image to ROS Image message
                image_msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
                image_msg.header.stamp = rospy.Time.now()
                image_msg.header.frame_id = "camera_frame"
                
                # Publish image
                self.image_pub.publish(image_msg)
                
            except CvBridgeError as e:
                rospy.logerr(f"CV Bridge Error: {e}")
        else:
            rospy.logwarn("Failed to capture frame")
    
    def shutdown(self):
        """
        Cleanup on shutdown
        """
        self.cap.release()
        rospy.loginfo("Camera Node Shutdown")

if __name__ == '__main__':
    try:
        node = CameraNode()
        rospy.on_shutdown(node.shutdown)
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
