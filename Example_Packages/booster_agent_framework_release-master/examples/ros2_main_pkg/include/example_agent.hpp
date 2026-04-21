#pragma once
#include "agent_node.hpp"

using namespace booster_agent_framework;

class ExampleAgent : public AgentNode {
public:
  ExampleAgent(const std::string &agent_id) : AgentNode(agent_id) {
    SetupComponents();
  }

private:
  void SetupComponents() {
    auto init_start_stamp = std::chrono::steady_clock::now();

    auto log_time_stamp = [this, init_start_stamp](std::string tag) {
      RCLCPP_INFO(get_logger(), "Till %s, init took: %ld ms", tag.c_str(),
                  std::chrono::duration_cast<std::chrono::milliseconds>(
                      std::chrono::steady_clock::now() - init_start_stamp)
                      .count());
    };
    log_time_stamp("before creating anything");
    // Create localized component names
    LocaleString wave_name({{"en", "Wave"}, {"zh", "挥手"}});
    LocaleString get_up_name({{"en", "Get Up"}, {"zh", "站立"}});

    // Create click callback
    auto click_callback =
        [node = this](const Component &clicked_component) -> OptionalToast {
      auto state_icon = clicked_component.As<DefaultStateIconComponent>();
      RCLCPP_INFO(node->get_logger(), "Component clicked: %s, state: %d",
                  state_icon->id().c_str(), state_icon->state());
      auto component = node->GetComponentMgr().GetComponent(state_icon->id());
      component->As<DefaultStateIconComponent>()->set_state(
          state_icon->state() ? false : true);
      node->GetComponentMgr().UpdateComponent(component);
      return LocaleString({{"en", "Clicked!"}, {"zh", "已点击!"}});
    };

    log_time_stamp("before creating components");

    // Create components
    std::vector<std::shared_ptr<DefaultStateIconComponent>> components{
        std::make_shared<DefaultStateIconComponent>(
            "wave", wave_name, "res/wave.png", false, click_callback,
            JoystickEvent::CreateEvent(JoystickEventType::kBUTTON_DOWN,
                                       {JoystickKey::kA})),
        std::make_shared<DefaultStateIconComponent>(
            "get_up", get_up_name, "res/get_up.png", false, click_callback,
            JoystickEvent::CreateEvent(JoystickEventType::kBUTTON_DOWN,
                                       {JoystickKey::kB}))};
    log_time_stamp("after creating components");
    this->GetComponentMgr().AddComponents(components);
    log_time_stamp("after adding components");
  }
};