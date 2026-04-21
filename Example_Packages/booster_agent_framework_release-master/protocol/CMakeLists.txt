cmake_minimum_required(VERSION 3.8)
project(booster_agent_framework_protocol)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)

# generate message files
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/AgentState.msg"
  "msg/ControllerState.msg"
  "srv/AgentService.srv"
  "srv/AgentJoyService.srv"
  DEPENDENCIES std_msgs
)

# export dependencies
ament_export_dependencies(rosidl_default_runtime)
ament_export_include_directories(include)

ament_package()
