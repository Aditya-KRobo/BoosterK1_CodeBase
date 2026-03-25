/**
 * @file component.cpp
 * @brief Implementation of Component system classes
 * @author Booster Robotics
 * @date 2025
 */

#include "component.hpp"
#include "agent_node.hpp"
#include <algorithm>

namespace booster_agent_framework {

// Component Implementation
Component::Component(const std::string &id, const LocaleString &name,
                     ComponentClickCallback click_callback,
                     JoystickEvent shortcut, const uint32_t display_sequence)
    : id_(id), name_(name), click_callback_(click_callback),
      shortcut_(shortcut), display_sequence_(display_sequence) {}

bool Component::Equal(const Component &other) const {
  return GetType() == other.GetType() && id() == other.id();
}

ComponentPtr Component::Clone() const {
  return std::make_shared<Component>(*this);
}

OptionalToast Component::OnClick(const ConstComponentPtr &clicked_component) {
  if (click_callback_) {
    return click_callback_(*clicked_component);
  }
  return std::nullopt;
}

json Component::ToJson([[maybe_unused]] const std::string &lang) const {
  json j;
  j["id"] = id();
  j["type"] = "component";
  // Currently return all translations
  j["locale_name"] = name().ToJson();
  return j;
}

// IconComponent Implementation
IconComponent::IconComponent(const std::string &id, const LocaleString &name,
                             const std::string &path,
                             ComponentClickCallback click_callback,
                             JoystickEvent shortcut,
                             const uint32_t display_sequence)
    : Component(id, name, click_callback, shortcut, display_sequence),
      path_(path) {}

bool IconComponent::Equal(const Component &other) const {
  return Component::Equal(other);
}

ComponentPtr IconComponent::Clone() const {
  return std::make_shared<IconComponent>(*this);
}

json IconComponent::ToJson(const std::string &lang) const {
  json j = Component::ToJson(lang);
  j["type"] = "icon_component";
  j["icon_resource_path"] = path();
  return j;
}

// StateIconComponent Implementation
StateIconComponent::StateIconComponent(const std::string &id,
                                       const LocaleString &name,
                                       const std::string &path, const int state,
                                       ComponentClickCallback click_callback,
                                       JoystickEvent shortcut,
                                       const uint32_t display_sequence)
    : IconComponent(id, name, path, click_callback, shortcut, display_sequence),
      state_(state) {}

bool StateIconComponent::Equal(const Component &other) const {
  if (!IconComponent::Equal(other)) {
    return false;
  }
  const auto *state_comp = dynamic_cast<const StateIconComponent *>(&other);
  return state_comp && state_ == state_comp->state_;
}

ComponentPtr StateIconComponent::Clone() const {
  return std::make_shared<StateIconComponent>(*this);
}

json StateIconComponent::ToJson(const std::string &lang) const {
  json j = IconComponent::ToJson(lang);
  j["type"] = "state_icon_component";
  j["state"] = state_;
  return j;
}

// DefaultStateIconComponent Implementation
DefaultStateIconComponent::DefaultStateIconComponent(
    const std::string &id, const LocaleString &name, const std::string &path,
    const bool state, ComponentClickCallback click_callback,
    JoystickEvent shortcut, const uint32_t display_sequence)
    : StateIconComponent(id, name, path, state ? 1 : 0, click_callback,
                         shortcut, display_sequence) {}

bool DefaultStateIconComponent::Equal(const Component &other) const {
  return StateIconComponent::Equal(other);
}

ComponentPtr DefaultStateIconComponent::Clone() const {
  return std::make_shared<DefaultStateIconComponent>(*this);
}

json DefaultStateIconComponent::ToJson(const std::string &lang) const {
  json j = StateIconComponent::ToJson(lang);
  j["type"] = "state_icon_component_default";
  return j;
}

// ComponentMgr Implementation
ComponentMgr::ComponentMgr(AgentNode *node) : node_(node) {
  if (!node_) {
    throw std::invalid_argument("AgentNode pointer cannot be null");
  }
}

ComponentPtr ComponentMgr::GetComponent(const std::string &id) {
  std::lock_guard<std::mutex> lock(mutex_);
  auto it = components_.find(id);
  return (it != components_.end()) ? it->second : nullptr;
}

std::vector<ComponentPtr> ComponentMgr::GetAllComponents() const {
  std::vector<ComponentPtr> result;
  result.reserve(components_.size());
  {
    std::lock_guard<std::mutex> lock(mutex_);
    for (const auto &pair : components_) {
      result.push_back(pair.second);
    }
  }

  // Sort by display sequence
  std::sort(result.begin(), result.end(),
            [](const ComponentPtr &a, const ComponentPtr &b) {
              if (a->display_sequence() != b->display_sequence()) {
                return a->display_sequence() < b->display_sequence();
              }
              return a->id() < b->id();
            });

  return result;
}

void ComponentMgr::AddComponent(const ComponentPtr &component) {
  if (!component)
    return;
  {
    std::lock_guard<std::mutex> lock(mutex_);
    if (components_.find(component->id()) != components_.end()) {
      RCLCPP_WARN(node_->get_logger(),
                  "Component added: %s, but already exists in component list. "
                  "It will be replaced.",
                  component->id().c_str());
    }
    components_[component->id()] = component;
    GenerateComponentSequence(component);
  }
  PublishComponents(component);
}

template <class T, typename = std::enable_if_t<std::is_base_of_v<Component, T>>>
void ComponentMgr::AddComponents(
    const std::vector<std::shared_ptr<T>> &components) {
  {
    std::lock_guard<std::mutex> lock(mutex_);
    for (const auto &component : components) {
      if (component) {
        components_[component->id()] = component;
        GenerateComponentSequence(component);
      }
    }
  }
  PublishComponents(nullptr);
}

// Explicitly instantiate for known types
template void ComponentMgr::AddComponents<Component>(
    const std::vector<std::shared_ptr<Component>> &);
template void ComponentMgr::AddComponents<IconComponent>(
    const std::vector<std::shared_ptr<IconComponent>> &);
template void ComponentMgr::AddComponents<StateIconComponent>(
    const std::vector<std::shared_ptr<StateIconComponent>> &);
template void ComponentMgr::AddComponents<DefaultStateIconComponent>(
    const std::vector<std::shared_ptr<DefaultStateIconComponent>> &);

void ComponentMgr::UpdateComponent(const ComponentPtr &component) {
  if (!component)
    return;
  ComponentPtr updated_component = nullptr;
  {
    std::lock_guard<std::mutex> lock(mutex_);
    auto it = components_.find(component->id());
    if (it != components_.end()) {
      updated_component = it->second = component;
    }
  }
  if (!updated_component) {
    RCLCPP_WARN(node_->get_logger(),
                "Component update: %s, but not found in component list.",
                component->id().c_str());
    return;
  }
  PublishComponents(updated_component);
}

void ComponentMgr::RemoveComponent(const ComponentPtr &component) {
  if (!component)
    return;
  {
    std::lock_guard<std::mutex> lock(mutex_);
    if (components_.find(component->id()) == components_.end()) {
      RCLCPP_WARN(node_->get_logger(),
                  "Component removed: %s, but not found in component list.",
                  component->id().c_str());
      return;
    }
    components_.erase(component->id());
  }
  PublishComponents(nullptr);
}

template <class T, typename = std::enable_if_t<std::is_base_of_v<Component, T>>>
void ComponentMgr::ReplaceComponents(
    const std::vector<std::shared_ptr<T>> &components) {
  {
    std::lock_guard<std::mutex> lock(mutex_);
    components_.clear();
    for (const auto &component : components) {
      if (component) {
        components_[component->id()] = component;
        GenerateComponentSequence(component);
      }
    }
  }
  PublishComponents(nullptr);
}

// Explicitly instantiate for known types
template void ComponentMgr::ReplaceComponents<Component>(
    const std::vector<std::shared_ptr<Component>> &);
template void ComponentMgr::ReplaceComponents<IconComponent>(
    const std::vector<std::shared_ptr<IconComponent>> &);
template void ComponentMgr::ReplaceComponents<StateIconComponent>(
    const std::vector<std::shared_ptr<StateIconComponent>> &);
template void ComponentMgr::ReplaceComponents<DefaultStateIconComponent>(
    const std::vector<std::shared_ptr<DefaultStateIconComponent>> &);

void ComponentMgr::PublishToast(LocaleString message) const {
  json protocol_message;
  protocol_message["agent_ui_components"] =
      GenerateProtocolMessageToast(message);
  node_->PublishMessage(protocol_message);
}

void ComponentMgr::GenerateComponentSequence(const ComponentPtr &component) {
  if (!component)
    return;
  // Generate a unique sequence number for the component with sequence equal to
  // ComponentDisplaySequenceAuto
  if (component->display_sequence() != ComponentDisplaySequenceAuto) {
    return;
  }
  int sequence = auto_display_sequence_index_++;
  component->set_display_sequence(sequence);
  RCLCPP_INFO(node_->get_logger(),
              "Generated component sequence: %x for component: %s", sequence,
              component->id().c_str());
}

OptionalToast
ComponentMgr::OnComponentClick(const ConstComponentPtr &clicked_component) {
  if (!clicked_component)
    return std::nullopt;
  RCLCPP_INFO(node_->get_logger(),
              "Component clicked: %s, call its OnClick func.",
              clicked_component->id().c_str());
  ComponentPtr component = GetComponent(clicked_component->id());
  if (!component) {
    RCLCPP_ERROR(node_->get_logger(),
                 "Component clicked: %s, but not found in component list.",
                 clicked_component->id().c_str());
    return std::nullopt;
  }
  return component->OnClick(clicked_component);
}

bool ComponentMgr::OnJoystickEvent(const JoystickEvent &joystick_event) {
  ComponentPtr component = nullptr;
  {
    std::lock_guard<std::mutex> lock(mutex_);
    // Find component with matching shortcut
    for (const auto &pair : components_) {
      if (pair.second->shortcut() == joystick_event) {
        component = pair.second;
        break;
      }
    }
  }
  if (component != nullptr) {
    // Toast is for single App client, will not publish for now.
    std::thread click_thread([component, this]() {
      OptionalToast toast = component->OnClick(component);
      RCLCPP_INFO(this->node_->get_logger(),
                  "OnJoystickEvent convert to clicked event, process complete. "
                  "Component: %s, ",
                  component->id().c_str());
    });
    click_thread.detach();
    return true;
  }
  return false;
}

void ComponentMgr::PublishComponents(const ComponentPtr &component) const {
  json protocol_message;
  protocol_message["agent_ui_components"] = GenerateProtocolMessage(component);
  node_->PublishMessage(protocol_message);
}

json ComponentMgr::GenerateProtocolMessage(const ComponentPtr &component,
                                           const std::string &lang) const {
  json j;
  std::vector<json> components_list;
  if (component) {
    j["components_list_type"] = "changed_components";
    components_list.emplace_back(component->ToJson(lang));
  } else {
    j["components_list_type"] = "all_components";
    auto components = GetAllComponents();
    for (const auto &com : components) {
      components_list.emplace_back(com->ToJson(lang));
    }
  }
  j["components_list"] = components_list;
  return j;
}

json ComponentMgr::GenerateProtocolMessageToast(const LocaleString &message,
                                                [[maybe_unused]] const std::string &lang) const {
  json j;
  std::vector<json> components_list;
  json toast_component;
  toast_component["id"] = "toast";
  toast_component["type"] = "toast_component";
  // Currently return all translations
  toast_component["locale_name"] = message.ToJson();
  components_list.emplace_back(toast_component);
  j["components_list_type"] = "changed_components";
  j["components_list"] = components_list;
  return j;
}

} // namespace booster_agent_framework
