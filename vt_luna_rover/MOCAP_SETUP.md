# Motion Capture System Setup Guide

## Overview

Your VT LUNA rover uses **external cameras mounted around the room** to track its position. This is called a **motion capture (mocap) system**. The cameras send position data to the rover via WiFi, allowing precise navigation.

## What is a Motion Capture System?

Think of it like this:
- **Room cameras** = Eyes watching from above
- **Rover** = Actor on a stage
- **WiFi** = How the cameras tell the rover where it is

The cameras track special markers on your rover and calculate its exact position (x, y) and orientation (which way it's facing).

## System Architecture

```
┌─────────────────────────────────────────┐
│     Room Cameras (Motion Capture)       │
│  - Track rover position from above      │
│  - Calculate x, y, orientation          │
└─────────────────┬───────────────────────┘
                  │ WiFi
                  ▼
┌─────────────────────────────────────────┐
│   Raspberry Pi (ROS)                    │
│  ┌────────────────────────────────────┐ │
│  │  Mocap Receiver Node               │ │
│  │  - Receives position via WiFi      │ │
│  └────────────┬───────────────────────┘ │
│               ▼                          │
│  ┌────────────────────────────────────┐ │
│  │  Navigation Controller             │ │
│  │  - Decides how to move             │ │
│  └────────────┬───────────────────────┘ │
│               ▼                          │
│  ┌────────────────────────────────────┐ │
│  │  Motor Controller                  │ │
│  │  - Sends commands to Arduino       │ │
│  └────────────┬───────────────────────┘ │
└───────────────┼─────────────────────────┘
                │ USB/Serial
                ▼
┌─────────────────────────────────────────┐
│           Arduino                        │
│  - Controls motors and servos           │
└─────────────────────────────────────────┘
```

## ROS Nodes Explained

### 1. **Mocap Receiver Node** 📡
**What it does**: Listens for position data from the room cameras via WiFi

**Input**: Position data over network (WiFi)
- Example: `{"id": "rover_1", "position": {"x": 1.5, "y": 2.3}, ...}`

**Output**: ROS messages with rover position
- Topic: `/mocap/pose` - Where the rover is

**File**: `mocap_receiver.py`

### 2. **Navigation Controller Node** 🧭
**What it does**: Uses position data to navigate to target locations

**Input**: 
- Current position from mocap (where am I?)
- Target location (where should I go?)

**Output**: Movement commands
- Topic: `/cmd_vel` - "Move forward 0.3 m/s, turn 0.5 rad/s"

**File**: `navigation_controller.py`

### 3. **Motor Controller Node** 🚗
**What it does**: Converts movement commands to motor speeds

**Input**: Movement commands from navigation
**Output**: Serial commands to Arduino
- Example: `MOVE:100,100` (both motors forward)

**File**: `motor_controller.py`

### 4. **Arduino** 🔧
**What it does**: Actually controls the motors and servos

**Input**: Serial commands from Raspberry Pi
**Output**: Electrical signals to motors

**File**: `arduino_motor_control.ino`

## How Nodes Talk to Each Other

Nodes communicate using **topics** (like radio channels):

```
Mocap Receiver → /mocap/pose → Navigation Controller
Navigation Controller → /cmd_vel → Motor Controller
Motor Controller → Serial → Arduino
```

## Setup Instructions

### 1. Motion Capture System Configuration

Your room cameras need to send data in this format:

**JSON Format** (recommended):
```json
{
  "id": "rover_1",
  "position": {
    "x": 1.5,
    "y": 2.3,
    "z": 0.0
  },
  "orientation": {
    "x": 0.0,
    "y": 0.0,
    "z": 0.0,
    "w": 1.0
  },
  "timestamp": 1234567890.123
}
```

**Network Settings**:
- Protocol: UDP
- Port: 5555 (configurable)
- IP: Raspberry Pi's WiFi IP address

### 2. Raspberry Pi WiFi Setup

```bash
# Connect to your WiFi network
sudo nmcli dev wifi connect "YourNetworkName" password "YourPassword"

# Find your IP address
hostname -I
# Example output: 192.168.1.100
```

Tell your mocap system to send data to this IP address.

### 3. Install ROS Package

```bash
# Copy the rover_control package
cd ~/catkin_ws/src
cp -r /Users/abi/-AK/vt_luna_rover/ros_ws/src/rover_control .

# Build
cd ~/catkin_ws
catkin_make

# Make scripts executable
chmod +x src/rover_control/scripts/*.py
```

### 4. Launch the System

```bash
# Start all nodes
roslaunch rover_control rover_control.launch

# Or with custom settings
roslaunch rover_control rover_control.launch \
  mocap_port:=5555 \
  rover_id:=rover_1 \
  serial_port:=/dev/ttyACM0
```

## Testing

### Test 1: Check Mocap Data Reception

```bash
# Terminal 1: Launch system
roslaunch rover_control rover_control.launch

# Terminal 2: Monitor position data
rostopic echo /mocap/pose
```

You should see position updates from the cameras.

### Test 2: Send Target Location

```bash
# Send rover to position (x=2.0, y=1.5)
rostopic pub /target_location geometry_msgs/Point "x: 2.0
y: 1.5
z: 0.0"

# Enable navigation
rostopic pub /navigation_enabled std_msgs/Bool "data: true"

# Monitor state
rostopic echo /nav_state
```

### Test 3: Check Motor Commands

```bash
# Monitor commands being sent to Arduino
rostopic echo /cmd_vel
```

## Common Motion Capture Systems

### OptiTrack / Motive
- Professional mocap system
- Exports data via NatNet protocol
- May need additional ROS package: `mocap_optitrack`

### Vicon
- Another professional system
- Use ROS package: `vicon_bridge`

### Custom/DIY System
- Use the provided `mocap_receiver.py`
- Configure your system to send JSON over UDP

## Troubleshooting

### No Position Data Received
1. Check WiFi connection: `ping <mocap_computer_ip>`
2. Check firewall: `sudo ufw allow 5555/udp`
3. Verify mocap system is sending to correct IP
4. Check port number matches

### Rover Not Moving
1. Check position data: `rostopic echo /mocap/pose`
2. Check navigation enabled: `rostopic echo /navigation_enabled`
3. Check motor commands: `rostopic echo /cmd_vel`
4. Test Arduino directly (see main SETUP_GUIDE.md)

### Position Data Jumpy/Noisy
1. Check mocap camera calibration
2. Ensure good lighting
3. Check for reflective surfaces interfering
4. Add filtering in navigation controller

## Coordinate System

Make sure your mocap system and rover use the same coordinate system:

```
      Y (forward)
      ↑
      │
      │
      └────→ X (right)
     
Rover at origin (0,0) facing forward (+Y direction)
```

## Sample Manipulation Workflow

1. **Setup**: Place sample at known location (e.g., x=2.0, y=1.5)
2. **Start System**: Launch ROS nodes
3. **Send Target**: Tell rover to go to sample location
4. **Navigate**: Rover uses mocap position to navigate
5. **Manipulate**: When reached, activate gripper/manipulator
6. **Return**: Send rover back to start position

## Example Commands

```bash
# Enable navigation
rostopic pub /navigation_enabled std_msgs/Bool "data: true"

# Go to sample location
rostopic pub /target_location geometry_msgs/Point "x: 2.0
y: 1.5
z: 0.0"

# Wait for rover to reach target...

# Stop navigation
rostopic pub /navigation_enabled std_msgs/Bool "data: false"
```

## Next Steps

1. **Calibrate** your motion capture system
2. **Mark** your rover with tracking markers
3. **Test** position tracking without movement
4. **Test** simple navigation (move 1 meter forward)
5. **Practice** sample manipulation routine

## Important Notes

⚠️ **Safety**:
- Test in open area first
- Have emergency stop ready
- Monitor position data quality

💡 **Tips**:
- Good lighting improves tracking
- Keep markers visible to cameras
- Start with slow speeds
- Calibrate mocap system regularly
