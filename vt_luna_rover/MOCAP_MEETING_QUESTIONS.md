# Motion Capture Meeting Questions
**Date:** Wednesday, February 18, 2026
**Who:** [Teammate Name] meeting with MoCap Grad Student
**Purpose:** Understand how to integrate the motion capture system with our rover (Raspberry Pi + ROS)

---

## 1. System Connection & Data Flow

- How does the motion capture system send position data to an external device (like our Raspberry Pi)?
  - Is it over **WiFi, Ethernet, or USB**?
  - What **protocol** is used? (VRPN, NatNet, ROS topic, UDP stream, etc.)
- What **IP address / network** does the mocap system broadcast on?
- Do we need to be on a specific **WiFi network** or plug into a specific **Ethernet port** in the lab?
- Is there a **ROS package** already set up to receive mocap data? (e.g., `vrpn_client_ros`)

## 2. Rover Tracking Setup

- What kind of **markers/reflectors** do we need to put on the rover?
  - How many markers minimum?
  - Where can we get the markers? Does the lab provide them?
- How do we **register/create a rigid body** for our rover in the mocap software?
  - Can we do this ourselves, or does the grad student need to set it up?
- What **data format** does the system output? (x, y, z position? quaternion/euler for rotation?)
- What is the **coordinate system**? (Which axis is up? Where is the origin in the room?)
- What is the **update rate** (how many times per second do we get position data)?

## 3. Room & Workspace Details

- What are the **exact dimensions** of the motion capture volume? (We heard 3m x 3m — confirm?)
- Are there any **dead zones** or areas with poor tracking?
- Can we put **obstacles or sand** on the floor for our rover testing?
- What is the **floor surface** like? (Flat, tiled, carpeted?)
- Are there **height restrictions**? (Clearance for our rover + markers)

## 4. Access & Scheduling

- What are the **lab hours**? When can our team come in to test?
- Do we need to **book time** in advance?
- Do we need any **training or certification** to use the lab?
- Who do we contact if something goes wrong during a session?
- Can we access the lab **on weekends**?

## 5. Software & Technical Details

- What **mocap software** is running? (Vicon Tracker, OptiTrack Motive, Qualisys, etc.)
- Is there a **computer in the lab** we can use, or do we bring our own?
- Can we run a **ROS node on the lab computer** or do we need to stream data to our Raspberry Pi?
- Is there sample code or a **tutorial** for connecting to the system?
- What **OS and ROS version** is the lab computer running?

## 6. Integration with Our Rover

- Our rover uses a **Raspberry Pi** running ROS with Arduino motor control.
  - What is the best way to get real-time position data to the Pi?
  - Recommended setup: Pi on same network → subscribe to mocap ROS topic?
- Is there any **latency** we should worry about between mocap measurement and data arrival?
- Can the system track **multiple objects** at once? (In case we add obstacles later)
- Has anyone else connected a **rover or robot** to this mocap system before? Any tips?

---

## Notes from Meeting
*(Fill in during/after the meeting)*

**Answers:**


**Action Items:**


**Follow-up Needed:**

