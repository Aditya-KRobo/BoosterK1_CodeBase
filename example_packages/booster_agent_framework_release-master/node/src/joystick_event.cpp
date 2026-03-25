/**
 * @file joystick.cpp
 * @brief Implementation of joystick event handling
 * @author Booster Robotics
 * @date 2025
 */

#include "joystick_event.hpp"
#include <sstream>

#include "booster_agent_framework_protocol/msg/controller_state.hpp"

namespace booster_agent_framework {

JoystickEvent
JoystickEvent::CreateEvent(JoystickEventType event_type,
                           std::initializer_list<JoystickKey> keys) {
  JoystickKeySet key_set_value = 0;
  for (const auto &key : keys) {
    key_set_value |= static_cast<JoystickKeySet>(key);
  }
  return JoystickEvent(event_type, key_set_value);
}

JoystickEvent::JoystickEvent(JoystickEventType event_type,
                             JoystickKeySet key_set, float axis_lx,
                             float axis_ly, float axis_rx, float axis_ry)
    : event_type_(event_type), key_set_(key_set), axis_lx_(axis_lx),
      axis_ly_(axis_ly), axis_rx_(axis_rx), axis_ry_(axis_ry) {}

JoystickEvent::JoystickEvent(
    const booster_agent_framework_protocol::msg::ControllerState &state)
    : event_type_(static_cast<JoystickEventType>(state.event)),
      axis_lx_(state.lx), axis_ly_(state.ly), axis_rx_(state.rx),
      axis_ry_(state.ry) {
  JoystickKeySet key_set = 0;
  if (state.a)
    key_set |= static_cast<JoystickKeySet>(JoystickKey::kA);
  if (state.b)
    key_set |= static_cast<JoystickKeySet>(JoystickKey::kB);
  if (state.x)
    key_set |= static_cast<JoystickKeySet>(JoystickKey::kX);
  if (state.y)
    key_set |= static_cast<JoystickKeySet>(JoystickKey::kY);
  if (state.lt)
    key_set |= static_cast<JoystickKeySet>(JoystickKey::kLT);
  if (state.rt)
    key_set |= static_cast<JoystickKeySet>(JoystickKey::kRT);
  if (state.lb)
    key_set |= static_cast<JoystickKeySet>(JoystickKey::kLB);
  if (state.rb)
    key_set |= static_cast<JoystickKeySet>(JoystickKey::kRB);
  if (state.ls)
    key_set |= static_cast<JoystickKeySet>(JoystickKey::kLS);
  if (state.rs)
    key_set |= static_cast<JoystickKeySet>(JoystickKey::kRS);
  // set kHAT_CENTER only for kHAT, cause all other event may carry kHAT_CENTER
  if (state.hat_c && event_type_ == JoystickEventType::kHAT)
    key_set |= static_cast<JoystickKeySet>(JoystickKey::kHAT_CENTER);
  if (state.hat_u)
    key_set |= static_cast<JoystickKeySet>(JoystickKey::kHAT_UP);
  if (state.hat_d)
    key_set |= static_cast<JoystickKeySet>(JoystickKey::kHAT_DOWN);
  if (state.hat_l)
    key_set |= static_cast<JoystickKeySet>(JoystickKey::kHAT_LEFT);
  if (state.hat_r)
    key_set |= static_cast<JoystickKeySet>(JoystickKey::kHAT_RIGHT);
  if (state.hat_lu)
    key_set |= static_cast<JoystickKeySet>(JoystickKey::kHAT_LEFT_UP);
  if (state.hat_ld)
    key_set |= static_cast<JoystickKeySet>(JoystickKey::kHAT_LEFT_DOWN);
  if (state.hat_ru)
    key_set |= static_cast<JoystickKeySet>(JoystickKey::kHAT_RIGHT_UP);
  if (state.hat_rd)
    key_set |= static_cast<JoystickKeySet>(JoystickKey::kHAT_RIGHT_DOWN);
  if (state.back)
    key_set |= static_cast<JoystickKeySet>(JoystickKey::kBACK);
  if (state.start)
    key_set |= static_cast<JoystickKeySet>(JoystickKey::kSTART);
  key_set_ = key_set;
}

bool JoystickEvent::operator==(const JoystickEvent &other) const {
  if (key_set_ != other.key_set_)
    return false;
  if (event_type_ == other.event_type_)
    return true;
  if (event_type_ == JoystickEventType::kBUTTON_DOWN_OR_HAT &&
      (other.event_type_ == JoystickEventType::kBUTTON_DOWN ||
       other.event_type_ == JoystickEventType::kHAT))
    return true;
  if (other.event_type_ == JoystickEventType::kBUTTON_DOWN_OR_HAT &&
      (event_type_ == JoystickEventType::kBUTTON_DOWN ||
       event_type_ == JoystickEventType::kHAT))
    return true;
  return false;
}

std::string JoystickEvent::ToString() const {
  std::stringstream ss;

  // Add event type
  ss << "JoystickEvent(type=";
  switch (event_type_) {
  case JoystickEventType::kNONE:
    ss << "NONE";
    break;
  case JoystickEventType::kAXIS:
    ss << "AXIS";
    break;
  case JoystickEventType::kHAT:
    ss << "HAT";
    break;
  case JoystickEventType::kBUTTON_DOWN:
    ss << "BUTTON_DOWN";
    break;
  case JoystickEventType::kBUTTON_UP:
    ss << "BUTTON_UP";
    break;
  case JoystickEventType::kREMOVE:
    ss << "REMOVE";
    break;
  default:
    ss << "UNKNOWN";
    break;
  }

  // Add key set
  ss << ", keys=0x" << std::hex << key_set_;

  // Add individual keys if any are pressed
  if (key_set_ != 0) {
    ss << " [";
    bool first = true;

    // Check each possible key
    static const std::pair<JoystickKey, const char *> keyNames[] = {
        {JoystickKey::kA, "A"},
        {JoystickKey::kB, "B"},
        {JoystickKey::kX, "X"},
        {JoystickKey::kY, "Y"},
        {JoystickKey::kLT, "LT"},
        {JoystickKey::kRT, "RT"},
        {JoystickKey::kLB, "LB"},
        {JoystickKey::kRB, "RB"},
        {JoystickKey::kLS, "LS"},
        {JoystickKey::kRS, "RS"},
        {JoystickKey::kHAT_CENTER, "HAT_CENTER"},
        {JoystickKey::kHAT_UP, "HAT_UP"},
        {JoystickKey::kHAT_DOWN, "HAT_DOWN"},
        {JoystickKey::kHAT_LEFT, "HAT_LEFT"},
        {JoystickKey::kHAT_RIGHT, "HAT_RIGHT"},
        {JoystickKey::kHAT_LEFT_UP, "HAT_LEFT_UP"},
        {JoystickKey::kHAT_LEFT_DOWN, "HAT_LEFT_DOWN"},
        {JoystickKey::kHAT_RIGHT_UP, "HAT_RIGHT_UP"},
        {JoystickKey::kHAT_RIGHT_DOWN, "HAT_RIGHT_DOWN"},
        {JoystickKey::kBACK, "BACK"},
        {JoystickKey::kSTART, "START"}};

    for (const auto &keyPair : keyNames) {
      if ((key_set_ & static_cast<JoystickKeySet>(keyPair.first)) != 0) {
        if (!first)
          ss << ", ";
        ss << keyPair.second;
        first = false;
      }
    }

    ss << "]";
  }

  // Add axis information if relevant
  if (event_type_ == JoystickEventType::kAXIS) {
    ss << ", axis(lx=" << axis_lx_ << ", ly=" << axis_ly_ << ", rx=" << axis_rx_
       << ", ry=" << axis_ry_ << ")";
  }

  ss << ")";
  return ss.str();
}

} // namespace booster_agent_framework
