# VT LUNA Rover - Sample Manipulation Project

This project demonstrates a rover control system using:
- **Raspberry Pi**: Running ROS (Robot Operating System) for high-level control
- **Arduino**: For low-level motor control and sensor interfacing
- **Motion Capture System**: External cameras mounted in the room track rover position via WiFi

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│          (Motion Capture System)           │
│  - Track rover position from above                      │
│  - Send position data via WiFi                          │
└────────────────────────┬────────────────────────────────┘
                         │ WiFi
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    Raspberry Pi (ROS)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Mocap Node   │  │ Navigation   │  │ Motor Ctrl   │  │
│  │ (Receiver)   │  │ Controller   │  │ Node         │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                    (Serial/USB Connection)
                            │
┌─────────────────────────────────────────────────────────┐
│                        Arduino                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Motor Driver │  │ Servo Control│  │ Sensor Read  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Prerequisites

### Raspberry Pi
- ROS Noetic (or ROS2 Humble)
- Python 3
- pyserial
- WiFi connection to motion capture system

### Arduino
- Arduino IDE
- Servo library
- Motor driver library (e.g., L298N)

### Motion Capture System
- Room cameras setup and calibrated
- Network connectivity (WiFi)
- Tracking markers on rover

## Installation

### On Raspberry Pi
```bash
# Install ROS dependencies
sudo apt-get install ros-noetic-geometry-msgs ros-noetic-nav-msgs
sudo apt-get install python3-serial

# Create ROS workspace
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

### On Arduino
1. Open Arduino IDE
2. Install required libraries (Servo, etc.)
3. Upload the `arduino_motor_control.ino` sketch

### Motion Capture System
1. Configure cameras to track rover
2. Set up WiFi network connection
3. Configure mocap system to send data to Raspberry Pi IP
4. See `MOCAP_SETUP.md` for detailed instructions

## Usage

1. Connect Arduino to Raspberry Pi via USB
2. Ensure WiFi connection to motion capture system
3. Launch ROS nodes:
```bash
roslaunch rover_control rover_control.launch
```

## Project Structure

- `arduino/` - Arduino sketches for motor and servo control
- `ros_ws/` - ROS workspace with nodes for mocap, navigation, and motor control
- `launch/` - ROS launch files
- `MOCAP_SETUP.md` - Motion capture system setup guide
- `SETUP_GUIDE.md` - General setup and troubleshooting

## Features

- Motor control via ROS messages
- Motion capture-based positioning and navigation
- Autonomous navigation to target locations
- WiFi-based position tracking
- Manual and autonomous control modes
