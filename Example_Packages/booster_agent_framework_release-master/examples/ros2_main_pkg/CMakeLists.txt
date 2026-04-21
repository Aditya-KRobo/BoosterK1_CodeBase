cmake_minimum_required(VERSION 3.8)
project(example_agent)
set(EXECUTABLE_NAME example_agent)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)

find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(booster_agent_framework_node REQUIRED)

# source files
file(GLOB SOURCE_FILES src/*.cpp)
add_executable(${EXECUTABLE_NAME} ${SOURCE_FILES})

set_property(TARGET ${EXECUTABLE_NAME} PROPERTY CXX_STANDARD 17)

include_directories(
  include
)

ament_target_dependencies(${EXECUTABLE_NAME} booster_agent_framework_node rclcpp sensor_msgs)

target_include_directories(${EXECUTABLE_NAME} PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>)
target_compile_features(${EXECUTABLE_NAME} PUBLIC c_std_99 cxx_std_17) # Require C99 and C++17

install(TARGETS
  ${EXECUTABLE_NAME}
  DESTINATION lib/${PROJECT_NAME})

install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME})

ament_package()
