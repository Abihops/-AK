#!/usr/bin/env python3

# VT LUNA Rover - Motor Bridge Node
# This ROS2 node sits between the navigation stack and the Arduino
# It takes cmd_vel from ROS and sends serial commands to the Arduino
#
# Subscribes to:
#   /cmd_vel              Twist   - drive commands from navigation
#   /mechanism/speed      Float32 - mechanism motor (-1.0 to 1.0)
#   /servo/angles         Float32MultiArray - 3 servo angles (0 to 180)
#
# Publishes:
#   /arduino/connected    Bool    - True if Arduino is responding
#
# Serial commands sent to Arduino:
#   DRIVE:left,right   speeds -255 to 255
#   MECH:speed         speed  -255 to 255
#   SERVO:s1,s2,s3     angles 0 to 180
#   STOP
#   PING  (Arduino replies PONG so we know its alive)

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool, Float32, Float32MultiArray
import serial
import serial.tools.list_ports
import threading
import time


class MotorBridge(Node):
    def __init__(self):
        super().__init__('motor_bridge')

        # Parameters you can change from a launch file
        self.declare_parameter('serial_port', '/dev/ttyACM0')
        self.declare_parameter('baud_rate', 115200)
        self.declare_parameter('wheel_base', 0.35)       # rover track width in meters
        self.declare_parameter('max_speed', 255)          # max PWM value 0-255
        self.declare_parameter('cmd_vel_timeout', 0.5)    # seconds before we send STOP

        self.port        = self.get_parameter('serial_port').value
        self.baud        = self.get_parameter('baud_rate').value
        self.wheel_base  = self.get_parameter('wheel_base').value
        self.max_spd     = self.get_parameter('max_speed').value
        self.cmd_timeout = self.get_parameter('cmd_vel_timeout').value

        # Open serial connection to Arduino
        self.ser = None
        self.serial_lock = threading.Lock()
        self.connect_serial()

        # Track when we last got a drive command so the watchdog works
        self.last_cmd_time = time.time()
        self.arduino_ok = False

        # Subscribers
        self.create_subscription(Twist,             '/cmd_vel',         self.cmd_vel_cb,  10)
        self.create_subscription(Float32,           '/mechanism/speed', self.mech_cb,     10)
        self.create_subscription(Float32MultiArray, '/servo/angles',    self.servo_cb,    10)

        # Publishers
        self.status_pub = self.create_publisher(Bool, '/arduino/connected', 10)

        # Timers
        self.create_timer(0.1,  self.watchdog_timer)    # 10Hz  - send STOP if cmd_vel dies
        self.create_timer(1.0,  self.ping_timer)        # 1Hz   - check Arduino is alive
        self.create_timer(0.05, self.read_serial_timer) # 20Hz  - read Arduino responses

        self.get_logger().info(f'Motor Bridge ready on {self.port} at {self.baud} baud')

    def connect_serial(self):
        # Try the default port first, then scan all USB ports if that fails
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=0.1)
            time.sleep(2.0)  # wait for Arduino to finish resetting
            self.get_logger().info(f'Connected to Arduino on {self.port}')
        except serial.SerialException:
            self.get_logger().warn(f'Could not open {self.port}, scanning for Arduino...')
            self.ser = self.find_arduino()

    def find_arduino(self):
        # Look through all USB serial ports for an Arduino
        for port in serial.tools.list_ports.comports():
            if 'Arduino' in (port.manufacturer or '') or 'ttyACM' in port.device or 'ttyUSB' in port.device:
                try:
                    s = serial.Serial(port.device, self.baud, timeout=0.1)
                    time.sleep(2.0)
                    self.get_logger().info(f'Found Arduino on {port.device}')
                    return s
                except serial.SerialException:
                    continue
        self.get_logger().error('No Arduino found - check USB cable')
        return None

    def send(self, cmd):
        # Thread safe serial write - returns True if it worked
        if self.ser is None or not self.ser.is_open:
            self.get_logger().warn('Serial not open, skipping command')
            return False
        with self.serial_lock:
            try:
                self.ser.write((cmd + '\n').encode('utf-8'))
                return True
            except serial.SerialException as e:
                self.get_logger().error(f'Serial write failed: {e}')
                return False

    def cmd_vel_cb(self, msg):
        # Convert Twist to left/right wheel speeds using unicycle model
        # linear.x is forward speed, angular.z is turn rate
        self.last_cmd_time = time.time()

        lin = msg.linear.x
        ang = msg.angular.z

        v_left  = lin - ang * (self.wheel_base / 2.0)
        v_right = lin + ang * (self.wheel_base / 2.0)

        # Normalize so neither side exceeds 1.0 before scaling to PWM
        max_v = max(abs(v_left), abs(v_right), 1.0)
        v_left  /= max_v
        v_right /= max_v

        left_pwm  = int(v_left  * self.max_spd)
        right_pwm = int(v_right * self.max_spd)

        # Right motors are physically mirrored so flip the sign
        right_pwm = -right_pwm

        left_pwm  = max(-255, min(255, left_pwm))
        right_pwm = max(-255, min(255, right_pwm))

        self.send(f'DRIVE:{left_pwm},{right_pwm}')

    def mech_cb(self, msg):
        # Mechanism motor expects a float from -1.0 to 1.0
        speed = int(max(-1.0, min(1.0, msg.data)) * self.max_spd)
        self.send(f'MECH:{speed}')

    def servo_cb(self, msg):
        # Expects an array of 3 angles in degrees (0 to 180)
        if len(msg.data) < 3:
            self.get_logger().warn('SERVO needs 3 values [s1, s2, s3]')
            return
        a1 = int(max(0, min(180, msg.data[0])))
        a2 = int(max(0, min(180, msg.data[1])))
        a3 = int(max(0, min(180, msg.data[2])))
        self.send(f'SERVO:{a1},{a2},{a3}')

    def watchdog_timer(self):
        # Send STOP if no drive command has come in for a while
        if time.time() - self.last_cmd_time > self.cmd_timeout:
            self.send('STOP')

    def ping_timer(self):
        # Ping the Arduino every second to see if its still there
        self.send('PING')

    def read_serial_timer(self):
        # Read any responses from Arduino and update connection status
        if self.ser is None or not self.ser.is_open:
            self.status_pub.publish(Bool(data=False))
            return
        with self.serial_lock:
            try:
                while self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8', errors='replace').strip()
                    if line:
                        if line == 'PONG' or line.startswith('OK') or line.startswith('READY'):
                            self.arduino_ok = True
                        elif line.startswith('ERR'):
                            self.get_logger().warn(f'Arduino error: {line}')
            except serial.SerialException as e:
                self.get_logger().error(f'Serial read failed: {e}')
                self.arduino_ok = False

        self.status_pub.publish(Bool(data=self.arduino_ok))

    def destroy_node(self):
        # Send a final stop before shutting down
        self.get_logger().info('Shutting down - sending STOP')
        self.send('STOP')
        if self.ser and self.ser.is_open:
            self.ser.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = MotorBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
