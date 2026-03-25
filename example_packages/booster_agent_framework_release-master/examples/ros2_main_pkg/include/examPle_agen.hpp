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

OptionalToast MyAgentNode::OnWaveClick(const Component &component) {
    // Perform action (e.g., send command to robot)
    RCLCPP_INFO(get_logger(), "Waving hand!");
    
    // Return a message to the user
    return LocaleString("Waving started", "开始挥手");
}

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