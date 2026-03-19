cmake_minimum_required(VERSION 3.5)
project(rover_control)

# Find ament and required packages
find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(cv_bridge REQUIRED)
find_package(image_transport REQUIRED)

# Install Python scripts
install(PROGRAMS
  scripts/motor_bridge.py
  scripts/navigation_controller.py
  scripts/mocap_receiver.py
  scripts/teleop_keyboard.py
  scripts/hardware_test.py
  scripts/fake_mocap.py
  DESTINATION lib/${PROJECT_NAME}
)

# Install launch files
install(DIRECTORY launch/
  DESTINATION share/${PROJECT_NAME}/launch
)

ament_package()
