# How to Use ROS - Beginner's Guide

## What is ROS?

**ROS (Robot Operating System)** is like a **communication system** for robot parts. It's not actually an operating system like Windows or macOS - it's more like a **framework** that helps different programs talk to each other.

Think of it like a **group chat app** for your robot:
- Each program is a **person** (called a "node")
- They send **messages** to each other
- They talk on different **channels** (called "topics")

## Key Concepts

### 1. Nodes 🤖
A **node** is a program that does one job.

**Your rover has these nodes:**
- `mocap_receiver` - Listens for position data from cameras
- `navigation_controller` - Decides where to move
- `motor_controller` - Sends commands to Arduino

### 2. Topics 📢
A **topic** is like a **radio channel** where nodes send/receive messages.

**Examples:**
- `/mocap/pose` - Position data from motion capture
- `/cmd_vel` - Movement commands (velocity)
- `/target_location` - Where the rover should go

### 3. Messages 💬
**Messages** are the actual data being sent.

**Example message on `/cmd_vel`:**
```
linear:
  x: 0.3    # Move forward at 0.3 m/s
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: 0.5    # Turn at 0.5 rad/s
```

## How Nodes Communicate

```
┌─────────────────┐         /mocap/pose          ┌─────────────────┐
│  Mocap Receiver │ ──────────────────────────> │   Navigation    │
│      Node       │                              │   Controller    │
└─────────────────┘                              └─────────────────┘
                                                          │
                                                          │ /cmd_vel
                                                          ▼
                                                  ┌─────────────────┐
                                                  │  Motor Control  │
                                                  │      Node       │
                                                  └─────────────────┘
```

## Basic ROS Commands

### Starting ROS

**1. Start the ROS Master** (the "manager" that connects everything)
```bash
roscore
```
Leave this running in its own terminal window.

**2. Launch Your Rover System**
```bash
# In a new terminal
roslaunch rover_control rover_control.launch
```

This starts all your nodes at once!

### Checking What's Running

**List all active nodes:**
```bash
rosnode list
```
Output:
```
/mocap_receiver
/navigation_controller
/motor_controller
```

**List all topics:**
```bash
rostopic list
```
Output:
```
/mocap/pose
/cmd_vel
/target_location
/navigation_enabled
```

**See what's being published on a topic:**
```bash
rostopic echo /mocap/pose
```
This shows live data - you'll see position updates scrolling by!

### Sending Commands

**Send a target location:**
```bash
rostopic pub /target_location geometry_msgs/Point "x: 2.0
y: 1.5
z: 0.0"
```

**Enable navigation:**
```bash
rostopic pub /navigation_enabled std_msgs/Bool "data: true"
```

**Manual control - move forward:**
```bash
rostopic pub /cmd_vel geometry_msgs/Twist "linear:
  x: 0.3
  y: 0.0
  z: 0.0
angular:
  x: 0.0
  y: 0.0
  z: 0.0"
```

**Stop the rover:**
```bash
rostopic pub /cmd_vel geometry_msgs/Twist "linear: {x: 0.0, y: 0.0, z: 0.0}
angular: {x: 0.0, y: 0.0, z: 0.0}"
```

### Monitoring

**Check message rate on a topic:**
```bash
rostopic hz /mocap/pose
```
Shows how many messages per second (should be ~30-100 Hz)

**See topic info:**
```bash
rostopic info /cmd_vel
```
Shows who's publishing and who's subscribing

**Check if a node is running:**
```bash
rosnode info /motor_controller
```

## Typical Workflow

### 1. **Setup** (one time)
```bash
# Install ROS (see SETUP_GUIDE.md)
# Build your workspace
cd ~/catkin_ws
catkin_make
source devel/setup.bash
```

### 2. **Every Time You Run**

**Terminal 1: Start ROS**
```bash
roscore
```

**Terminal 2: Launch Rover**
```bash
roslaunch rover_control rover_control.launch
```

**Terminal 3: Monitor (optional)**
```bash
# Watch position data
rostopic echo /mocap/pose

# Or watch motor commands
rostopic echo /cmd_vel
```

**Terminal 4: Send Commands**
```bash
# Enable autonomous mode
rostopic pub /navigation_enabled std_msgs/Bool "data: true"

# Send target
rostopic pub /target_location geometry_msgs/Point "x: 2.0, y: 1.5, z: 0.0"
```

### 3. **Shutdown**
```bash
# In any terminal
Ctrl+C

# Or kill all ROS nodes
rosnode kill -a
```

## Common ROS Tools

### rqt_graph - Visualize Connections
```bash
rosrun rqt_graph rqt_graph
```
Shows a diagram of all nodes and how they're connected!

### rqt_console - View Logs
```bash
rosrun rqt_console rqt_console
```
See all error messages and warnings in one place

### rostopic pub - Send Messages
```bash
rostopic pub /topic_name message_type "data"
```

### rostopic echo - Read Messages
```bash
rostopic echo /topic_name
```

## Understanding Your Launch File

Your `rover_control.launch` file starts multiple nodes:

```xml
<node name="mocap_receiver" pkg="rover_control" type="mocap_receiver.py">
  <param name="mocap_port" value="5555" />
</node>
```

This means:
- **name**: Node will be called `mocap_receiver`
- **pkg**: It's in the `rover_control` package
- **type**: Run the `mocap_receiver.py` script
- **param**: Set parameter `mocap_port` to 5555

## Debugging Tips

### Node Won't Start
```bash
# Check if node file is executable
ls -l ~/catkin_ws/src/rover_control/scripts/
# Should show -rwxr-xr-x (x means executable)

# If not executable:
chmod +x ~/catkin_ws/src/rover_control/scripts/*.py
```

### Can't Find Package
```bash
# Make sure workspace is sourced
source ~/catkin_ws/devel/setup.bash

# Add to ~/.bashrc to do automatically:
echo "source ~/catkin_ws/devel/setup.bash" >> ~/.bashrc
```

### No Data on Topic
```bash
# Check who's publishing
rostopic info /topic_name

# If no publishers, the node might have crashed
rosnode list
```

### Serial Port Permission Denied
```bash
# Give permission
sudo chmod 666 /dev/ttyACM0

# Or add user to dialout group (permanent fix)
sudo usermod -a -G dialout $USER
# Then logout and login again
```

## Quick Reference

| Command | What it does |
|---------|-------------|
| `roscore` | Start ROS master |
| `roslaunch pkg file.launch` | Start multiple nodes |
| `rosnode list` | Show running nodes |
| `rostopic list` | Show all topics |
| `rostopic echo /topic` | See messages on topic |
| `rostopic pub /topic type "data"` | Send message to topic |
| `rostopic hz /topic` | Check message rate |
| `rosnode kill /node` | Stop a node |
| `Ctrl+C` | Stop current program |

## Example: Complete Session

```bash
# Terminal 1
roscore

# Terminal 2
roslaunch rover_control rover_control.launch

# Terminal 3 - Check everything is running
rosnode list
# Should see: /mocap_receiver, /navigation_controller, /motor_controller

# Check topics
rostopic list
# Should see: /mocap/pose, /cmd_vel, etc.

# Watch position data
rostopic echo /mocap/pose

# Terminal 4 - Control the rover
# Enable navigation
rostopic pub /navigation_enabled std_msgs/Bool "data: true"

# Send target location
rostopic pub /target_location geometry_msgs/Point "x: 2.0
y: 1.5
z: 0.0"

# Watch it go!
```

## Next Steps

1. ✅ Read this guide
2. ✅ Try basic commands (`rosnode list`, `rostopic list`)
3. ✅ Launch your rover system
4. ✅ Send simple commands
5. ✅ Monitor topics with `rostopic echo`
6. ✅ Try autonomous navigation

## More Resources

- **ROS Wiki**: http://wiki.ros.org/
- **ROS Tutorials**: http://wiki.ros.org/ROS/Tutorials
- **Your Setup Guide**: See `MOCAP_SETUP.md` and `SETUP_GUIDE.md`

---

**Remember**: ROS is just a way for programs to talk to each other. Each node does one job, and they communicate by sending messages on topics. That's it! 🚀
