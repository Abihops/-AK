#!/usr/bin/env python3
"""
VT LUNA Rover - ROS Motor Controller Node

This node receives velocity commands and sends them to Arduino
via serial connection.
"""

import rospy
import serial
import time
from geometry_msgs.msg import Twist
from std_msgs.msg import Int16MultiArray

class MotorController:
    def __init__(self):
        rospy.init_node('motor_controller', anonymous=False)
        
        # Parameters
        self.serial_port = rospy.get_param('~serial_port', '/dev/ttyACM0')
        self.baud_rate = rospy.get_param('~baud_rate', 115200)
        self.wheel_base = rospy.get_param('~wheel_base', 0.3)  # meters
        self.max_speed = rospy.get_param('~max_speed', 255)
        
        # Initialize serial connection
        try:
            self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
            time.sleep(2)  # Wait for Arduino to reset
            rospy.loginfo(f"Connected to Arduino on {self.serial_port}")
        except serial.SerialException as e:
            rospy.logerr(f"Failed to connect to Arduino: {e}")
            return
        
        # Subscribers
        self.cmd_vel_sub = rospy.Subscriber('/cmd_vel', Twist, self.cmd_vel_callback)
        self.servo_sub = rospy.Subscriber('/servo_cmd', Int16MultiArray, self.servo_callback)
        
        # Publishers (for feedback)
        self.status_pub = rospy.Publisher('/motor_status', Int16MultiArray, queue_size=10)
        
        rospy.loginfo("Motor Controller Node Started")
        
    def cmd_vel_callback(self, msg):
        """
        Convert Twist message to differential drive motor commands
        """
        linear_vel = msg.linear.x  # Forward/backward velocity (m/s)
        angular_vel = msg.angular.z  # Rotational velocity (rad/s)
        
        # Differential drive kinematics
        # v_left = v - (w * L) / 2
        # v_right = v + (w * L) / 2
        v_left = linear_vel - (angular_vel * self.wheel_base) / 2.0
        v_right = linear_vel + (angular_vel * self.wheel_base) / 2.0
        
        # Convert to motor PWM values (-255 to 255)
        left_pwm = int(self.velocity_to_pwm(v_left))
        right_pwm = int(self.velocity_to_pwm(v_right))
        
        # Send command to Arduino
        self.send_motor_command(left_pwm, right_pwm)
        
    def velocity_to_pwm(self, velocity):
        """
        Convert velocity (m/s) to PWM value (-255 to 255)
        Adjust this based on your motor characteristics
        """
        # Simple linear mapping (adjust based on calibration)
        max_velocity = 1.0  # m/s
        pwm = (velocity / max_velocity) * self.max_speed
        return max(min(pwm, self.max_speed), -self.max_speed)
    
    def send_motor_command(self, left_speed, right_speed):
        """
        Send motor command to Arduino
        """
        command = f"MOVE:{left_speed},{right_speed}\n"
        try:
            self.ser.write(command.encode())
            response = self.ser.readline().decode().strip()
            if response.startswith("OK"):
                rospy.logdebug(f"Motor command sent: {command.strip()}")
            else:
                rospy.logwarn(f"Arduino response: {response}")
        except Exception as e:
            rospy.logerr(f"Serial communication error: {e}")
    
    def servo_callback(self, msg):
        """
        Control servo positions
        msg.data = [pan_angle, tilt_angle]
        """
        if len(msg.data) >= 2:
            pan_angle = msg.data[0]
            tilt_angle = msg.data[1]
            self.send_servo_command(pan_angle, tilt_angle)
    
    def send_servo_command(self, pan_angle, tilt_angle):
        """
        Send servo command to Arduino
        """
        command = f"SERVO:{pan_angle},{tilt_angle}\n"
        try:
            self.ser.write(command.encode())
            response = self.ser.readline().decode().strip()
            rospy.logdebug(f"Servo command sent: {command.strip()}")
        except Exception as e:
            rospy.logerr(f"Serial communication error: {e}")
    
    def stop(self):
        """
        Stop all motors
        """
        try:
            self.ser.write(b"STOP\n")
            rospy.loginfo("Motors stopped")
        except Exception as e:
            rospy.logerr(f"Error stopping motors: {e}")
    
    def shutdown(self):
        """
        Cleanup on shutdown
        """
        self.stop()
        if self.ser.is_open:
            self.ser.close()
        rospy.loginfo("Motor Controller Node Shutdown")

if __name__ == '__main__':
    try:
        controller = MotorController()
        rospy.on_shutdown(controller.shutdown)
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
