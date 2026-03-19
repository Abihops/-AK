# VT LUNA Rover - Software Team Presentation Slides

---

## Slide 1: Title Slide

**VT LUNA Rover**  
**Software Team Progress Report**

Sample Manipulation Project  
February 12, 2026

---

## Slide 2: Current Status Overview

### ✅ Completed
- System architecture designed
- All core software modules written
- Comprehensive documentation created
- Ready for hardware integration

### ⏳ Waiting On
- Final mechanical design specifications
- Motor model selection
- Wheel base dimensions

---

## Slide 3: What is ROS?

**ROS = Robot Operating System**

Think of it as a **communication system** for robot parts

- Not an actual OS (like Windows/Mac)
- Framework that helps programs talk to each other
- Industry standard (NASA, Boston Dynamics, etc.)

**Key Concept:** Break one big program into small, independent programs

---

## Slide 4: Node-Based Communication

### Traditional Approach ❌
```
┌─────────────────────┐
│  One Giant Program  │
│  Does Everything    │
└─────────────────────┘
```
- Hard to test
- Hard to debug
- Hard to modify

### ROS Approach ✅
```
┌──────┐  ┌──────┐  ┌──────┐
│Node 1│  │Node 2│  │Node 3│
│Camera│→ │Brain │→ │Motor │
└──────┘  └──────┘  └──────┘
```
- Easy to test each part
- Easy to replace parts
- Runs in parallel

---

## Slide 5: Our System Architecture

```
┌─────────────────────────────┐
│  Motion Capture Cameras     │
│  (Room-mounted)             │
└──────────────┬──────────────┘
               │ WiFi
               ▼
┌─────────────────────────────┐
│  Raspberry Pi (ROS)         │
│  ┌────────┐  ┌────────┐    │
│  │ Mocap  │→ │  Nav   │→   │
│  │ Node   │  │ Node   │    │
│  └────────┘  └────────┘    │
│              ┌────────┐    │
│              │ Motor  │    │
│              │ Node   │    │
│              └────┬───┘    │
└───────────────────┼────────┘
                    │ Serial
                    ▼
┌─────────────────────────────┐
│  Arduino                    │
│  (Motor Control)            │
└─────────────────────────────┘
```

---

## Slide 6: Software Modules Completed

### 1. Motion Capture Receiver
- Receives rover position via WiFi
- Supports JSON/binary formats
- **Status:** ✅ Prototype complete

### 2. Navigation Controller
- Autonomous path planning
- State machine (Rotate → Move → Reached)
- **Status:** ✅ Prototype complete

### 3. Motor Controller
- ROS ↔ Arduino bridge
- Velocity → Motor speed conversion
- **Status:** ✅ Prototype complete

### 4. Arduino Control
- Low-level motor/servo control
- Serial command parsing
- **Status:** ✅ Prototype complete

---

## Slide 7: How Nodes Communicate

**Example: Moving the Rover**

1. **Mocap Node** receives position from cameras
   - Publishes to `/mocap/pose` topic

2. **Navigation Node** reads position
   - Calculates where to go
   - Publishes to `/cmd_vel` topic

3. **Motor Node** reads velocity command
   - Sends to Arduino via serial
   - Arduino moves motors

**All happening automatically in real-time!**

---

## Slide 8: Key Benefits of Our Approach

### 🔓 Modularity
Each component is independent

### 🧪 Testability  
Can test each node separately

### ♻️ Flexibility
Easy to swap components (e.g., different cameras)

### ⚡ Scalability
Simple to add new features

### 🏆 Industry Standard
Same architecture as professional robotics companies

---

## Slide 9: Documentation Created

✅ **Setup Guide** - Installation & configuration  
✅ **Motion Capture Setup** - Camera system integration  
✅ **ROS Usage Guide** - Beginner tutorial  
✅ **README** - Quick start guide  
✅ **Progress Report** - Detailed status

**All documentation ready for team use!**

---

## Slide 10: Why We're Ready

### Proactive Development Strategy

Instead of waiting idle, we:
1. ✅ Designed complete system architecture
2. ✅ Wrote all core software modules
3. ✅ Made code configurable for any hardware
4. ✅ Created comprehensive documentation

### Result:
**Rapid integration once hardware is finalized!**

No software delays during integration phase.

---

## Slide 11: Next Steps

### Immediate (This Week)
- Code review
- Simulation testing
- Documentation review

### Upon Hardware Specs
- Parameter calibration
- Arduino integration
- Motion capture testing

### Before Presentation
- Autonomous navigation demo
- Manual control backup
- Performance tuning

---

## Slide 12: Technical Highlights

### What Makes This Impressive

- **Motion Capture Integration**: Advanced positioning system
- **WiFi-Based Tracking**: No onboard sensors needed
- **ROS Framework**: Professional robotics platform
- **Modular Architecture**: Industry best practices
- **Comprehensive Docs**: Knowledge transfer ready

---

## Slide 13: Risk Mitigation

| Risk | Our Solution |
|------|--------------|
| Hardware delays | ✅ Code ready for quick integration |
| Mocap unavailable | ✅ Can switch to onboard camera |
| Motor compatibility | ✅ Configurable for any driver |
| Integration issues | ✅ Modular = test independently |

---

## Slide 14: Questions?

**We're ready to discuss:**
- System architecture details
- Integration timeline
- Hardware requirements
- Testing strategy

---

## Slide 15: Summary

### Software Team Status: ✅ ON TRACK

**Completed:**
- 4 major software modules
- Complete documentation suite
- Flexible, configurable architecture

**Ready For:**
- Immediate integration upon hardware finalization
- Testing and validation
- Presentation demonstration

**Timeline:** No delays expected

---

# Presentation Tips

## What to Say for Each Slide:

### Slide 3 (What is ROS):
*"ROS is like a communication system for robot parts. Instead of one huge program, we break it into small programs called 'nodes' that talk to each other. This is what NASA and Boston Dynamics use."*

### Slide 4 (Node-Based):
*"Think of it like a team. Instead of one person doing everything, each person has a specific job and they communicate. This makes it easier to test and fix problems."*

### Slide 5 (Architecture):
*"Here's our system. Room cameras track the rover and send position via WiFi. The Raspberry Pi has three nodes that work together: one receives position, one decides where to go, and one controls the motors."*

### Slide 6 (Modules):
*"We've completed all four major software components. Even though we're waiting on hardware specs, we wrote the code to be configurable, so we can quickly adjust once we know the final design."*

### Slide 10 (Why Ready):
*"Instead of waiting idle, we took a proactive approach. We designed everything and wrote prototype code. This means zero software delays when hardware is ready - we just plug in the specs and go."*

---

# Visual Suggestions

- Use **green checkmarks** (✅) for completed items
- Use **clock icons** (⏳) for waiting items
- Keep diagrams **simple and clear**
- Use **arrows** to show data flow
- **Bold** key terms
- Use **bullet points** not paragraphs

---

# Key Message

**"We've been productive and strategic during the hardware design phase, ensuring rapid integration and zero software delays."**
