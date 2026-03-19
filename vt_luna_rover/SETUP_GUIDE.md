# VT LUNA Rover - Setup Guide

## Hardware Setup

### Arduino Connections

#### Motor Driver (L298N)
- **ENA** → Arduino Pin 5 (PWM)
- **IN1** → Arduino Pin 7
- **IN2** → Arduino Pin 8
- **ENB** → Arduino Pin 6 (PWM)
- **IN3** → Arduino Pin 9
- **IN4** → Arduino Pin 10
- **12V** → External power supply
- **GND** → Common ground with Arduino
- **OUT1, OUT2** → Left motor
- **OUT3, OUT4** → Right motor

#### Servos
- **Pan Servo** → Arduino Pin 11
- **Tilt Servo** → Arduino Pin 12
- **5V** → Arduino 5V
- **GND** → Arduino GND

#### Power
- Arduino powered via USB from Raspberry Pi
- Motors powered by separate 12V battery
- **Important**: Connect grounds together

### Raspberry Pi Setup

1. **Install ROS Noetic** (Ubuntu 20.04):
```bash
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
sudo apt install curl
curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -
sudo apt update
sudo apt install ros-noetic-desktop-full
echo "source /opt/ros/noetic/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

2. **Install Dependencies**:
```bash
sudo apt install python3-rosdep python3-rosinstall python3-rosinstall-generator python3-wstool build-essential
sudo apt install ros-noetic-cv-bridge ros-noetic-image-transport
sudo apt install python3-opencv python3-serial python3-pip
pip3 install pyserial
```

3. **Setup ROS Workspace**:
```bash
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws
catkin_make
source devel/setup.bash
echo "source ~/catkin_ws/devel/setup.bash" >> ~/.bashrc
```

4. **Copy Rover Control Package**:
```bash
cp -r /path/to/vt_luna_rover/ros_ws/src/rover_control ~/catkin_ws/src/
cd ~/catkin_ws
catkin_make
chmod +x ~/catkin_ws/src/rover_control/scripts/*.py
```

## Software Setup

### Arduino

1. Open Arduino IDE
2. Install Servo library (usually pre-installed)
3. Open `arduino_motor_control.ino`
4. Select your Arduino board (Tools → Board)
5. Select the correct port (Tools → Port)
6. Upload the sketch

### Testing Arduino Connection

After uploading, open Serial Monitor (115200 baud):
- You should see: "Arduino Ready - VT LUNA Rover"
- Test commands:
  - `MOVE:100,100` - Both motors forward
  - `MOVE:-100,-100` - Both motors backward
  - `SERVO:90,90` - Center servos
  - `STOP` - Stop all motors

### ROS Configuration

1. **Find Arduino Port**:
```bash
ls /dev/ttyACM*
# or
ls /dev/ttyUSB*
```

2. **Give Permission** (if needed):
```bash
sudo chmod 666 /dev/ttyACM0
# Or add user to dialout group:
sudo usermod -a -G dialout $USER
# Then logout and login again
```

3. **Test Camera**:
```bash
ls /dev/video*
# Test with:
cheese  # or
ffplay /dev/video0
```

## Running the System

### Full System Launch

```bash
# Terminal 1: Start roscore
roscore

# Terminal 2: Launch all nodes
roslaunch rover_control rover_control.launch

# Optional: Specify custom serial port and camera
roslaunch rover_control rover_control.launch serial_port:=/dev/ttyACM0 camera_id:=0
```

### Individual Node Testing

```bash
# Test motor controller only
rosrun rover_control motor_controller.py

# Test camera only
rosrun rover_control camera_node.py

# Test vision processing
rosrun rover_control vision_node.py

# Test autonomous control
rosrun rover_control autonomous_control.py
```

## Manual Control

### Using Command Line

```bash
# Move forward
rostopic pub /cmd_vel geometry_msgs/Twist "linear:
  x: 0.3
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: 0.0"

# Rotate in place
rostopic pub /cmd_vel geometry_msgs/Twist "linear:
  x: 0.0
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: 0.5"

# Control servos
rostopic pub /servo_cmd std_msgs/Int16MultiArray "data: [90, 45]"
```

### Enable Autonomous Mode

```bash
# Enable autonomous sample manipulation
rostopic pub /autonomous_mode std_msgs/Bool "data: true"

# Disable
rostopic pub /autonomous_mode std_msgs/Bool "data: false"
```

## Monitoring

### View Camera Feed

```bash
# Install if needed
sudo apt install ros-noetic-rqt-image-view

# View raw camera
rqt_image_view /camera/image_raw

# View processed image with detections
rqt_image_view /camera/image_processed
```

### Monitor Topics

```bash
# List all active topics
rostopic list

# Monitor target detection
rostopic echo /target_detected

# Monitor target position
rostopic echo /target_position

# Monitor rover state
rostopic echo /rover_state
```

## Calibration

### Color Detection

Edit `vision_node.py` to adjust HSV color ranges for your target object:

```python
# For red objects
target_color_lower: [0, 100, 100]
target_color_upper: [10, 255, 255]

# For blue objects
target_color_lower: [100, 100, 100]
target_color_upper: [130, 255, 255]

# For green objects
target_color_lower: [40, 100, 100]
target_color_upper: [80, 255, 255]
```

### Motor Speed Calibration

Adjust in `motor_controller.py`:
```python
max_velocity = 1.0  # Adjust based on your motors
```

### Servo Tracking

Adjust gains in `vision_node.py`:
```python
kp_x = 0.1  # Pan gain
kp_y = 0.1  # Tilt gain
```

## Troubleshooting

### Arduino Not Responding
- Check USB connection
- Verify correct port in launch file
- Check baud rate (115200)
- Reset Arduino

### Camera Not Working
- Check camera ID: `ls /dev/video*`
- Test with: `cheese` or `ffplay`
- Verify permissions

### Motors Not Moving
- Check power supply
- Verify motor driver connections
- Test with Serial Monitor commands
- Check motor driver enable pins

### ROS Nodes Crashing
- Check dependencies: `rosdep check rover_control`
- Verify Python version (Python 3)
- Check file permissions: `chmod +x scripts/*.py`

## Next Steps

1. **Tune Parameters**: Adjust speeds, color ranges, and control gains
2. **Add Features**: Implement gripper control, additional sensors
3. **Test Scenarios**: Practice sample collection in controlled environment
4. **Document**: Record successful configurations and behaviors

## Safety Notes

⚠️ **Important Safety Reminders**:
- Always have emergency stop ready
- Test in open area first
- Monitor battery levels
- Keep hands clear of moving parts
- Use appropriate power supplies
