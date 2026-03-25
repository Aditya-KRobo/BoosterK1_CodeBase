/**
 * @file joystick_event.hpp
 * @brief Joystick event handling system for Booster agent framework
 * @author Booster Robotics
 * @date 2025
 */

#pragma once
#include "booster_agent_framework_protocol/msg/controller_state.hpp"
#include <initializer_list>
#include <string>

namespace booster_agent_framework {

/**
 * @brief Enumeration of joystick event types
 */
enum class JoystickEventType : uint32_t {
  kNONE = 0,                  ///< No event occurred
  kAXIS = 0x600,              ///< Analog stick/axis motion event
  kHAT = 0x602,               ///< D-pad/hat position change event
  kBUTTON_DOWN = 0x603,       ///< Button press event
  kBUTTON_UP = 0x604,         ///< Button release event
  kREMOVE = 0x606,            ///< Device removal event
  kBUTTON_DOWN_OR_HAT = 0x800 ///< Custom value for button down or hat
};

/**
 * @brief Enumeration of joystick keys/buttons
 *
 * Each key is represented as a bit flag to allow combining multiple keys
 * into a single key set using bitwise OR operations.
 */
enum class JoystickKey : uint32_t {
  kNONE = 0x0,                 ///< No key pressed
  kA = 0x1 << 0,               ///< A button
  kB = 0x1 << 1,               ///< B button
  kX = 0x1 << 2,               ///< X button
  kY = 0x1 << 3,               ///< Y button
  kLT = 0x1 << 4,              ///< Left trigger
  kRT = 0x1 << 5,              ///< Right trigger
  kLB = 0x1 << 6,              ///< Left bumper
  kRB = 0x1 << 7,              ///< Right bumper
  kLS = 0x1 << 8,              ///< Left stick click
  kRS = 0x1 << 9,              ///< Right stick click
  kHAT_CENTER = 0x1 << 10,     ///< D-pad center position
  kHAT_UP = 0x1 << 11,         ///< D-pad up
  kHAT_DOWN = 0x1 << 12,       ///< D-pad down
  kHAT_LEFT = 0x1 << 13,       ///< D-pad left
  kHAT_RIGHT = 0x1 << 14,      ///< D-pad right
  kHAT_LEFT_UP = 0x1 << 15,    ///< D-pad left-up diagonal
  kHAT_LEFT_DOWN = 0x1 << 16,  ///< D-pad left-down diagonal
  kHAT_RIGHT_UP = 0x1 << 17,   ///< D-pad right-up diagonal
  kHAT_RIGHT_DOWN = 0x1 << 18, ///< D-pad right-down diagonal
  kBACK = 0x1 << 19,           ///< Back button (reserved)
  kSTART = 0x1 << 20,          ///< Start button (reserved)
};

/// @brief Type alias for a set of joystick keys represented as a bitmask
using JoystickKeySet = uint32_t;

/**
 * @brief Represents a joystick event with key state and optional axis data
 *
 * JoystickEvent encapsulates all information about a joystick input event
 * including the event type, which keys are pressed, and analog stick positions.
 */
class JoystickEvent {
public:
  /**
   * @brief Get a static instance representing no joystick event
   * @return JoystickEvent with kNONE type and no keys pressed
   */
  static JoystickEvent NONE() {
    static JoystickEvent _none_event(JoystickEventType::kNONE, 0);
    return _none_event;
  }

  /**
   * @brief Create a JoystickEvent from an event type and list of keys
   * @param event_type The type of joystick event
   * @param keys Initializer list of JoystickKey values to combine
   * @return JoystickEvent with the specified type and combined key set
   */
  static JoystickEvent CreateEvent(JoystickEventType event_type,
                                   std::initializer_list<JoystickKey> keys);

  /**
   * @brief Construct a JoystickEvent with event type and key set
   * @param event_type The type of joystick event
   * @param key_set Bitmask representing pressed keys
   */
  JoystickEvent(JoystickEventType event_type, JoystickKeySet key_set)
      : event_type_(event_type), key_set_(key_set){};

  /**
   * @brief Construct a JoystickEvent with event type, key set, and axis data
   * @param event_type The type of joystick event
   * @param key_set Bitmask representing pressed keys
   * @param axis_lx Left stick X axis value (-1.0 to 1.0)
   * @param axis_ly Left stick Y axis value (-1.0 to 1.0)
   * @param axis_rx Right stick X axis value (-1.0 to 1.0)
   * @param axis_ry Right stick Y axis value (-1.0 to 1.0)
   */
  JoystickEvent(JoystickEventType event_type, JoystickKeySet key_set,
                float axis_lx, float axis_ly, float axis_rx, float axis_ry);

  /**
   * @brief Construct a JoystickEvent from a ControllerState message
   * @param state The ControllerState message to convert from
   */
  JoystickEvent(
      const booster_agent_framework_protocol::msg::ControllerState &state);

  /**
   * @brief Check if this event contains a specific joystick key
   * @param key The joystick key to check for
   * @return true if the key is pressed in this event, false otherwise
   */
  bool HasKey(JoystickKey key) const {
    return (key_set_ & static_cast<JoystickKeySet>(key)) != 0;
  }

  /**
   * @brief Equality comparison operator
   * @param other The other JoystickEvent to compare against
   * @return true if events are equal, false otherwise
   */
  bool operator==(const JoystickEvent &other) const;

  /**
   * @brief Inequality comparison operator
   * @param other The other JoystickEvent to compare against
   * @return true if events are not equal, false otherwise
   */
  bool operator!=(const JoystickEvent &other) const {
    return !(*this == other);
  }

  /**
   * @brief Convert the joystick event to a string representation
   * @return String describing the event
   */
  std::string ToString() const;

  /// @brief The type of joystick event
  JoystickEventType event_type_;

  /// @brief Bitmask of pressed keys
  JoystickKeySet key_set_;

  /// @brief Left stick X axis value (-1.0 to 1.0)
  float axis_lx_ = 0.0f;

  /// @brief Left stick Y axis value (-1.0 to 1.0)
  float axis_ly_ = 0.0f;

  /// @brief Right stick X axis value (-1.0 to 1.0)
  float axis_rx_ = 0.0f;

  /// @brief Right stick Y axis value (-1.0 to 1.0)
  float axis_ry_ = 0.0f;
};
} // namespace booster_agent_framework