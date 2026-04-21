/**
 * @file agent_node.hpp
 * @brief Agent node implementation for Booster agent framework
 * @author Booster Robotics
 * @date 2025
 */

#pragma once
#include "booster_agent_framework_protocol/msg/agent_state.hpp"
#include "booster_agent_framework_protocol/msg/controller_state.hpp"
#include "booster_agent_framework_protocol/srv/agent_joy_service.hpp"
#include "booster_agent_framework_protocol/srv/agent_service.hpp"
#include "component.hpp"
#include <rclcpp/rclcpp.hpp>

namespace booster_agent_framework {
/// @brief Shared pointer to a Component object
using ComponentPtr = std::shared_ptr<Component>;

/**
 * @brief Base agent node that encapsulates common logic for communication with
 * Booster RPC service and dispatching UI component events.
 *
 * This class provides the base functionality for agent nodes including:
 * - Component management through ComponentMgr
 * - Joystick event handling
 * - ROS2 service interfaces for agent communication
 * - Publishing agent state information
 *
 * Derived classes must implement logic for handling component click and
 * component query events.
 */
class AgentNode : public rclcpp::Node {
public:
  /**
   * @brief Construct agent node with unique identifier
   * @param agent_id Unique identifier for this agent instance
   *
   * Initializes the agent node with necessary ROS2 publishers, services, and
   * callback groups. The agent_id is used to create unique service and topic
   * names.
   */
  AgentNode(const std::string &agent_id);

  /**
   * @brief Virtual destructor
   */
  virtual ~AgentNode() = default;

  /**
   * @brief Get reference to the component manager
   * @return Reference to ComponentMgr instance
   */
  ComponentMgr &GetComponentMgr() { return component_mgr_; }

protected:
  /**
   * @brief Handle joystick events
   * @param joystick_event The joystick event to handle
   * @return true if event was handled successfully, false otherwise
   *
   * If joystick event not handled by any component, this function then will be
   * called. This virtual function can be implemented by derived classes to
   * define how joystick events should be processed. The default implementation
   * returns false.
   */
  virtual bool OnJoystickEvent(const JoystickEvent &joystick_event);

private:
  /**
   * @brief Callback for general agent service requests
   * @param request The incoming service request
   * @param response The outgoing service response
   */
  void AgentMgrGeneralCallback(
      const std::shared_ptr<
          booster_agent_framework_protocol::srv::AgentService::Request>
          request,
      std::shared_ptr<
          booster_agent_framework_protocol::srv::AgentService::Response>
          response);

  /**
   * @brief Callback for joystick-related agent service requests
   * @param request The incoming joystick service request
   * @param response The outgoing joystick service response
   */
  void AgentMgrJoystickCallback(
      const std::shared_ptr<
          booster_agent_framework_protocol::srv::AgentJoyService::Request>
          request,
      std::shared_ptr<
          booster_agent_framework_protocol::srv::AgentJoyService::Response>
          response);

  /**
   * @brief Publish JSON message to all App clients via ROS2 topic
   * @param message The JSON message content to publish
   *
   * This method publishes messages to the agent's broadcast topic using
   * the AgentState message format defined in the protocol package.
   */
  void PublishMessage(const json &message) const;

protected:
  /// @brief Component manager for handling UI components
  ComponentMgr component_mgr_;

private:
  /// @brief Unique identifier for this agent
  std::string agent_id_;

  /// @brief Callback group for general server operations
  rclcpp::CallbackGroup::SharedPtr general_server_cb_group_;

  /// @brief Callback group for joystick server operations
  rclcpp::CallbackGroup::SharedPtr joystick_server_cb_group_;

  /// @brief Callback group for publishing operations
  rclcpp::CallbackGroup::SharedPtr publish_client_cb_group_;

  /// @brief Service server for general agent operations
  rclcpp::Service<booster_agent_framework_protocol::srv::AgentService>::
      SharedPtr general_server_;

  /// @brief Service server for joystick operations
  rclcpp::Service<booster_agent_framework_protocol::srv::AgentJoyService>::
      SharedPtr joystick_server_;

  /// @brief Publisher for agent state messages
  rclcpp::Publisher<booster_agent_framework_protocol::msg::AgentState>::
      SharedPtr publish_client_;

  /// @brief Timer for node readiness
  rclcpp::TimerBase::SharedPtr node_ready_timer_;

  /// @brief Flag indicating whether the node is ready
  std::atomic<bool> node_ready_{false};

  /// @brief Grant ComponentMgr access to private members for event handling
  friend class ComponentMgr;
};

} // end of namespace booster_agent_framework