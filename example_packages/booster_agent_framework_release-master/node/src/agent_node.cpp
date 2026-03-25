/**
 * @file agent_node.cpp
 * @brief Implementation of AgentNode class
 * @author Booster Robotics
 * @date 2025
 */

#include "agent_node.hpp"
#include <chrono>
#include <rclcpp/rclcpp.hpp>

namespace booster_agent_framework {

json ParseRequest(const std::string &request_body, std::string &lang) {
  // Parse request content per design at
  // https://booster.feishu.cn/wiki/GCM9wAuBziv2UIkqvxmciH3Dnne
  json request_json = json::parse(request_body);
  if (!request_json.contains("agent_req") ||
      !request_json["agent_req"].is_object()) {
    throw std::invalid_argument(
        "Invalid format: agent_req missing or not an object");
  }
  if (request_json.contains("language") &&
      request_json["language"].is_string()) {
    lang = request_json["language"].get<std::string>();
  }
  const auto &agent_req = request_json["agent_req"];
  if (!agent_req.contains("event") || !agent_req["event"].is_string()) {
    throw std::invalid_argument("Missing or invalid field: event");
  }

  const std::string event = agent_req["event"].get<std::string>();
  if (event == "on_component_click") {
    // If the event is "on_component_click", both "component_id" and "state"
    // must be present
    if (!agent_req.contains("component_id") ||
        !agent_req["component_id"].is_string() ||
        !agent_req.contains("state") ||
        !agent_req["state"].is_number_integer()) {
      throw std::invalid_argument("Missing fields: component_id / state");
    }
  } else if (event == "get_agent_ui_component_list") {

  } else
    throw std::invalid_argument("Unknown event type: " + event);
  return agent_req;
}

ComponentPtr ConstructComponentContext(ComponentPtr component,
                                       const json &request_json) {
  ComponentPtr clicked_component = component->Clone();
  if (!clicked_component) {
    throw std::invalid_argument("Failed to create clicked component");
  }
  switch (component->GetType()) {
  case ComponentType::kSTATE_ICON:
  case ComponentType::kDEFAULT_STATE_ICON:
    clicked_component->As<StateIconComponent>()->set_state(
        request_json["state"].get<int>());
  default:
    break;
  }
  return clicked_component;
}

AgentNode::AgentNode(const std::string &agent_id)
    : rclcpp::Node(SanitizeString(agent_id)), component_mgr_(this),
      agent_id_(agent_id) {
  auto init_start_stamp = std::chrono::steady_clock::now();

  auto log_time_stamp = [this, init_start_stamp](std::string tag) {
    RCLCPP_INFO(get_logger(), "Till %s, init took: %ld ms", tag.c_str(),
                std::chrono::duration_cast<std::chrono::milliseconds>(
                    std::chrono::steady_clock::now() - init_start_stamp)
                    .count());
  };

  log_time_stamp("before creating callback groups");
  // Create callback groups
  general_server_cb_group_ =
      this->create_callback_group(rclcpp::CallbackGroupType::MutuallyExclusive);
  joystick_server_cb_group_ =
      this->create_callback_group(rclcpp::CallbackGroupType::MutuallyExclusive);
  publish_client_cb_group_ =
      this->create_callback_group(rclcpp::CallbackGroupType::MutuallyExclusive);
  if (!general_server_cb_group_ || !joystick_server_cb_group_ ||
      !publish_client_cb_group_) {
    throw std::runtime_error("Failed to create callback groups");
  }

  log_time_stamp("before creating general_server_");
  // Create all service servers
  std::string general_server_name =
      std::string("/booster/agent/") + SanitizeString(agent_id) + "/service";
  general_server_ =
      this->create_service<booster_agent_framework_protocol::srv::AgentService>(
          general_server_name,
          std::bind(&AgentNode::AgentMgrGeneralCallback, this,
                    std::placeholders::_1, std::placeholders::_2),
          rmw_qos_profile_services_default, general_server_cb_group_);
  if (!general_server_) {
    throw std::runtime_error("Failed to create general server service");
  }
  RCLCPP_INFO(get_logger(), "Create general server service with name: %s",
              general_server_name.c_str());

  log_time_stamp("before creating joystick_server_");
  std::string joystick_server_name =
      std::string("/booster/agent/") + SanitizeString(agent_id) + "/joystick";
  joystick_server_ = this->create_service<
      booster_agent_framework_protocol::srv::AgentJoyService>(
      joystick_server_name,
      std::bind(&AgentNode::AgentMgrJoystickCallback, this,
                std::placeholders::_1, std::placeholders::_2),
      rmw_qos_profile_services_default, joystick_server_cb_group_);
  if (!joystick_server_) {
    throw std::runtime_error("Failed to create joystick server service");
  }
  RCLCPP_INFO(get_logger(), "Create joystick server service with name: %s",
              joystick_server_name.c_str());

  log_time_stamp("before creating publish_client_");
  std::string publish_client_name =
      std::string("/booster/agent/event_broadcast");
  rclcpp::PublisherOptions pub_opts;
  pub_opts.callback_group = publish_client_cb_group_;
  publish_client_ =
      this->create_publisher<booster_agent_framework_protocol::msg::AgentState>(
          publish_client_name, rclcpp::QoS(1), pub_opts);
  if (!publish_client_) {
    throw std::runtime_error("Failed to create publish client");
  }
  RCLCPP_INFO(get_logger(), "Create publish client with name: %s",
              publish_client_name.c_str());

  log_time_stamp("before creating node_ready_timer_");
  node_ready_timer_ = this->create_wall_timer(
      std::chrono::milliseconds(50), [this, init_start_stamp]() {
        auto wait_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
                           std::chrono::steady_clock::now() - init_start_stamp)
                           .count();
        if (publish_client_->get_subscription_count() == 0) {
          if (wait_ms <= 10000) {
            RCLCPP_INFO(get_logger(),
                        "No subscription found, node not registered to fastDDS "
                        "yet, init took: %ld ms",
                        wait_ms);
            return;
          } else {
            RCLCPP_WARN(get_logger(),
                        "Waited for %ld ms, still no subscription found, "
                        "proceeding anyway",
                        wait_ms);
          }
        }
        RCLCPP_INFO(get_logger(),
                    "Before publishing components, init took: %ld ms", wait_ms);
        node_ready_timer_->cancel();
        node_ready_.store(true);
        this->GetComponentMgr().PublishComponents(nullptr);
      });
  log_time_stamp("All complete");

  RCLCPP_INFO(get_logger(), "AgentNode initialized with ID: %s",
              agent_id_.c_str());
}

bool AgentNode::OnJoystickEvent([[maybe_unused]] const JoystickEvent &joystick_event) {
  // Handle joystick event
  return false; // Default implementation does nothing
}

void AgentNode::AgentMgrGeneralCallback(
    const std::shared_ptr<
        booster_agent_framework_protocol::srv::AgentService::Request>
        request,
    std::shared_ptr<
        booster_agent_framework_protocol::srv::AgentService::Response>
        response) {
  RCLCPP_INFO(get_logger(), "Received general request, body=%s",
              request->body.c_str());

  json response_json{{"success", true},
                     {"agent_api_level", kAgentFrameworkApiLevel}};

  try {
    std::string lang;
    json request_json = ParseRequest(request->body, lang);
    if (request_json["event"] == "on_component_click") {
      RCLCPP_INFO(
          get_logger(),
          "Processing on_component_click event, component_id=%s, state=%d",
          request_json["component_id"].get<std::string>().c_str(),
          request_json["state"].get<int>());
      ComponentPtr component = component_mgr_.GetComponent(
          request_json["component_id"].get<std::string>());
      if (!component) {
        throw std::invalid_argument(
            "Component not found, id: " +
            request_json["component_id"].get<std::string>());
      }
      RCLCPP_INFO(get_logger(), "Found component: id=%s, type=%d",
                  component->id().c_str(),
                  static_cast<int>(component->GetType()));
      // Construct copy of clicked component and assign context of request
      const ConstComponentPtr clicked_component =
          ConstructComponentContext(component, request_json);
      if (!clicked_component) {
        throw std::invalid_argument("Failed to construct clicked component");
      }
      RCLCPP_INFO(get_logger(),
                  "Constructed clicked component context: id=%s, state=%d",
                  clicked_component->id().c_str(),
                  clicked_component->As<StateIconComponent>()->state());
      OptionalToast toast = component_mgr_.OnComponentClick(clicked_component);
      if (toast.has_value()) {
        response_json["result"] =
            component_mgr_.GenerateProtocolMessageToast(toast.value(), lang);
      } else {
        response_json["result"] = json::object();
      }
    } else if (request_json["event"] == "get_agent_ui_component_list") {
      response_json["result"] =
          component_mgr_.GenerateProtocolMessage(nullptr, lang);
    } else {
      throw std::invalid_argument("Unknown event type: " +
                                  request_json["event"].get<std::string>());
    }
  } catch (const std::exception &e) {
    RCLCPP_ERROR(get_logger(), "Exception in general callback: %s", e.what());
    if (response_json.contains("result")) {
      response_json.erase("result");
    }
    response_json["success"] = false;
    response_json["error"] = std::string(e.what());
  }

  response->body = response_json.dump();

  RCLCPP_INFO(get_logger(), "Processed general request, response body=%s",
              response->body.c_str());
}

void AgentNode::AgentMgrJoystickCallback(
    const std::shared_ptr<
        booster_agent_framework_protocol::srv::AgentJoyService::Request>
        request,
    std::shared_ptr<
        booster_agent_framework_protocol::srv::AgentJoyService::Response>
        response) {
  RCLCPP_INFO(get_logger(), "Received joystick request, body size=%ld",
              request->body.size());

  try {
    if (request->body.size() !=
        sizeof(booster_agent_framework_protocol::msg::ControllerState)) {
      throw std::invalid_argument(
          "Invalid joystick request body size, expected: " +
          std::to_string(
              sizeof(booster_agent_framework_protocol::msg::ControllerState)) +
          ", actual: " + std::to_string(request->body.size()));
    }

    booster_agent_framework_protocol::msg::ControllerState state;
    std::memcpy(&state, request->body.data(), request->body.size());

    JoystickEvent joystick_event(state);
    RCLCPP_INFO(get_logger(), "Parsed joystick event: %s",
                joystick_event.ToString().c_str());

    bool handled = component_mgr_.OnJoystickEvent(joystick_event);
    if (handled) {
      RCLCPP_INFO(get_logger(), "Joystick event handled by component manager");
    } else if (this->OnJoystickEvent(joystick_event)) {
      RCLCPP_INFO(get_logger(), "Joystick event handled by agent node");
    } else {
      RCLCPP_INFO(get_logger(), "Joystick event not handled.");
    }
    response->body = 0;
  } catch (const std::exception &e) {
    RCLCPP_ERROR(get_logger(), "Exception in joystick callback: %s", e.what());
    response->body = 500;
  }
  RCLCPP_INFO(get_logger(), "Processed joystick request, response body=%d",
              response->body);
}

void AgentNode::PublishMessage(const json &message) const {
  if (!node_ready_.load()) {
    RCLCPP_WARN(get_logger(), "Node not ready, skip publishing message");
    return;
  }
  json j;
  // Now we have only this event
  j["event"] = "agent_ui_components_changed";
  j["agent_api_level"] = kAgentFrameworkApiLevel;
  j["body"] = message;

  auto publish_message = booster_agent_framework_protocol::msg::AgentState();
  publish_message.agent_id = agent_id_;
  publish_message.body = j.dump();
  publish_client_->publish(publish_message);
  RCLCPP_INFO(get_logger(), "Published message to App clients: %s",
              publish_message.body.c_str());
}

} // namespace booster_agent_framework