# Booster Agent Development Guide

## 1. Introduction

The **Booster Agent Framework** is a C++ based development framework designed to simplify the creation of interactive agents for Booster Robotics robots. Built on top of **ROS2**, it provides a robust set of tools for:

*   **UI Component Management**: Easily create and manage interactive UI elements (icons, buttons) that appear on the client application.
*   **Input Handling**: Unified handling of joystick/controller inputs and mapping them to actions.
*   **Internationalization**: Built-in support for multi-language text (e.g., English and Chinese).

## 2. Framework API Overview

The framework is located in `booster_agent_framework` and provides several key classes:

### 2.1. AgentNode (`agent_node.hpp`)
The `AgentNode` class is the backbone of any agent. It inherits from `rclcpp::Node` and handles:
*   Communication with the Booster Agent Manager.
*   Dispatching joystick events.
*   Managing the lifecycle of UI components.

**Key Methods:**
*   `AgentNode(const std::string &agent_id)`: Constructor.
*   `GetComponentMgr()`: Returns the `ComponentMgr` to add/remove/update UI components.
*   `OnJoystickEvent(const JoystickEvent &event)`: Virtual method to handle raw joystick events not consumed by components.

### 2.2. Component (`component.hpp`)
Component represents a UI element(a clickable button) on the mobile app.
*   **Types**: `kICON` (stateless), `kSTATE_ICON` (integer state), `kDEFAULT_STATE_ICON` (boolean state).
*   **Properties**: ID, Name (localized), Icon path, Click callback, Shortcut key.

#### 2.2.1. Icon Component
Simple clickable icon with image path. Mobile App will recognize this type of component and represents its component icon.

```cpp
auto icon = std::make_shared<IconComponent>(
    "my_icon", 
    LocaleString("My Icon"),
    "/path/to/icon.png",
    callback_function
);
```

#### 2.2.2. State Icon Component  
Icon with integer state (useful for multi-state toggles). Mobile App will represent this type of components' icon and carry component's state value when it's clicked.

```cpp
auto state_icon = std::make_shared<StateIconComponent>(
    "state_icon",
    LocaleString("State Icon"), 
    "/path/to/icon.png",
    0, // Initial state
    callback_function
);
```

#### 2.2.3. Default State Icon Component
Icon with boolean state (simple on/off). Mobile App will represent this type of components' icon and carry component's state value when it's clicked. When the component state is `true`, the icon in mobile app will be displayed as "on", otherwise as "off".

```cpp
auto toggle = std::make_shared<DefaultStateIconComponent>(
    "toggle",
    LocaleString("Toggle"),
    "/path/to/icon.png", 
    false, // Initially off
    callback_function
);
```
### 2.3. JoystickEvent (`joystick_event.hpp`)
Encapsulates controller inputs.
*   **Events**: Button Down/Up, Axis Move, Hat (D-Pad) Move.
*   **Keys**: `kA`, `kB`, `kX`, `kY`, `kLT`, `kRT`, `kHAT_UP`, etc.
*   **Helper**: `JoystickEvent::CreateEvent(...)` to easily define shortcuts (e.g., `LT + A`).

### 2.4. LocaleString (`types.hpp`)
Helper class for internationalization.
*   Stores strings for multiple languages (default `en`, supports `zh`).
*   Automatically serves the correct language to the client.

## 3. Step-by-Step: Building a Booster Agent

This section guides you through creating a new agent.

### Prerequisites
*   **ROS2**: Ubuntu 22.04 with ROS2 Humble installed.
*   **Booster Agent Framework**: Installed.
*   **Third-party Packages**: `sudo apt install -y libfuse2 libfuse3 jq`


### Step 1: Create a ROS2 Package
Create a ROS2 package for your agent by copying code of example agent.

### Step 2: Define Your Agent Node
Define a class that inherits from `booster_agent_framework::AgentNode`. You can update example_agent.hpp as follows:

```cpp
#include "booster_agent_framework/node/include/agent_node.hpp"
#include "booster_agent_framework/node/include/component.hpp"
using namespace booster_agent_framework;

class MyAgentNode : public AgentNode {
public:
    MyAgentNode() : AgentNode("com.company.my_awesome_agent") {
        InitComponents();
    }

private:
    void InitComponents();
    OptionalToast OnWaveClick(const Component &component);
};
```

### Step 3: Implement Component Logic
Define what happens when a component is clicked. The callback returns an `OptionalToast` (a message to show on screen) or `std::nullopt`.

```cpp
OptionalToast MyAgentNode::OnWaveClick(const Component &component) {
    // Perform action (e.g., send command to robot)
    RCLCPP_INFO(get_logger(), "Waving hand!");
    
    // Return a message to the user
    return LocaleString("Waving started", "开始挥手");
}
```

### Step 4: Register Components
Initialize your components and register them with the `ComponentMgr`.

```cpp
void MyAgentNode::InitComponents() {
    auto &mgr = GetComponentMgr();
    std::vector<std::shared_ptr<DefaultStateIconComponent>> my_components;

    // Create a "Wave" button
    // - ID: "wave_btn"
    // - Name: "Wave" (EN/ZH)
    // - Callback: OnWaveClick
    // - Shortcut: Button A
    auto wave_btn = std::make_shared<DefaultStateIconComponent>(
        "wave_btn", LocaleString("Wave", "挥手"), "res/wave.png", false,
        std::bind(&MyAgentNode::OnWaveClick, this, std::placeholders::_1),
        JoystickEvent::CreateEvent(JoystickEventType::kBUTTON_DOWN, {JoystickKey::kA})
    );

    my_components.push_back(wave_btn);

    // Update the manager with the list of components
    mgr.ReplaceComponents(my_components);
}
```

### Step 5: Main Entry Point
Update the `main` function to spin the node.

```cpp
int main(int argc, char *argv[]) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<MyAgentNode>();
    rclcpp::executors::MultiThreadedExecutor exec(rclcpp::ExecutorOptions(), 3);
    exec.add_node(node);
    RCLCPP_INFO(node->get_logger(), "Starting executor...");
    exec.spin();
    rclcpp::shutdown();
    return 0;
}
```

### Step 6: Configuration (`agent.json`)
Update an `agent.json` file in your package to define agent metadata. This is used by the system to load your agent.

```json
{
    "id": "com.company.my_awesome_agent",
    "name": "My Awesome Agent",
    "version": "1.0.0",
    "description": "An example agent",
    "gait": "default",
    "app_image" : {
        "icon" : "/res/icon.png"
    },
    "ros2" : {
        "package_name" : "my_awesome_agent",
        "launch_file" : "launch.py"
    }
}
```

Update CMakeLists.txt to assign project name and executable name.

```cmake
......
project(my_awesome_agent)
set(EXECUTABLE_NAME my_awesome_agent)
......
```

Update following lines to package.xml to assign package name:

```xml
  <name>my_awesome_agent</name>
  <version>1.0.0</version>
  <description>my_awesome_agent</description>
  <maintainer email="foo@bar.com">Foo Bar</maintainer>
```

### Step 7: Build
Build your package using `build_agent.sh`.
```bash
./booster_agent_framework/scripts/build_agent.sh path_to/my_awesome_agent
```

### Step 8: Install agent to robot
Install your agent to the robot using `install_agent.sh`.

If you're installing the agent locally, run:
```bash
./booster_agent_framework/scripts/install_agent.sh path_to/my_awesome_agent
```
Or if you're installing the agent to a remote robot, run:
```bash
./booster_agent_framework/scripts/install_agent.sh path_to/my_awesome_agent booster@<robot_perception_ip>
```

## 4. Advanced Features

### Dynamic Component Updates
You can update components at runtime. For example, to change the state of a toggle button:

```cpp
// Assuming you have a pointer to a DefaultStateIconComponent
my_toggle_component_->set_state(true); // Set state to ON

GetComponentMgr().UpdateComponent(my_toggle_component_);
```

### Handling Raw Joystick Events
Override `OnJoystickEvent` to handle inputs that aren't bound to specific components.

```cpp
bool MyAgentNode::OnJoystickEvent(const JoystickEvent &event) {
    if (event.IsButtonDown(JoystickKey::kB)) {
        // Handle B button press
        return true; // Event handled
    }
    return false; // Event not handled
}
```
### Booster Interface Integration
Booster Agent Framework only provides a set of APIs to interact with mobile apps.
In most situations, you also need [booster_robotics_sdk](https://github.com/BoosterRobotics/booster_robotics_sdk) or [booster_robotics_sdk_ros2](https://github.com/BoosterRobotics/booster_robotics_sdk_ros2) to control robot action or query robot status etc. Please refer corresponding documentation for more details.

#### Robot Status Integration
Your can subscribe to robot status topics (e.g., `booster_interface::msg::RobotStatesMsg`) to enable/disable components based on the robot's current mode (e.g., disable "Walk" button when robot is in "Prepare" or "Damp" mode).
