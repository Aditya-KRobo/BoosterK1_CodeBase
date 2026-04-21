/**
 * @file component.hpp
 * @brief Component system for Booster agent framework UI elements
 * @author Booster Robotics
 * @date 2025
 */

#pragma once
#include "joystick_event.hpp"
#include "types.hpp"
#include <atomic>
#include <functional>
#include <limits>
#include <memory>
#include <mutex>
#include <optional>
#include <string>
#include <unordered_map>

namespace booster_agent_framework {

class AgentNode;
class Component;

/// @brief Shared pointer to a Component object
using ComponentPtr = std::shared_ptr<Component>;

/// @brief Const shared pointer to a Component object
using ConstComponentPtr = std::shared_ptr<const Component>;

/// @brief Optional toast message that can be returned from component operations
using OptionalToast = std::optional<LocaleString>;

/// @brief Callback function type for component click events
using ComponentClickCallback = std::function<OptionalToast(const Component &)>;

/// @brief Default click callback that does nothing
static inline ComponentClickCallback click_callback_empty =
    [](const Component &) { return std::nullopt; };

/// @brief Special value indicating automatic display sequence assignment
constexpr static uint32_t ComponentDisplaySequenceAuto =
    std::numeric_limits<uint32_t>::max();

/**
 * @brief Enumeration of component types available in the framework
 */
enum class ComponentType : uint16_t {
  kNONE = 0,              ///< No component type
  kICON = 1,              ///< Simple icon component
  kSTATE_ICON = 2,        ///< Icon component with integer state
  kDEFAULT_STATE_ICON = 3 ///< Icon component with boolean state
};

/**
 * @brief Base class for all UI components in the agent framework
 *
 * Components represent interactive UI elements that users can click on.
 * Each component has an ID, name, optional keyboard shortcut, and click
 * callback.
 */
class Component : public std::enable_shared_from_this<Component> {
public:
  /**
   * @brief Construct a new Component
   * @param id Unique identifier for the component
   * @param name Localized name of the component
   * @param click_callback Function to call when component is clicked
   * @param shortcut Optional joystick shortcut for the component
   * @param display_sequence Order in which component should be displayed
   */
  Component(const std::string &id, const LocaleString &name,
            ComponentClickCallback click_callback = click_callback_empty,
            JoystickEvent shortcut = JoystickEvent::NONE(),
            const uint32_t display_sequence = ComponentDisplaySequenceAuto);

  /**
   * @brief Virtual destructor
   */
  virtual ~Component() = default;

  /**
   * @brief Get the component's unique ID
   * @return The component ID
   */
  const std::string &id() const { return id_; }

  /**
   * @brief Get the component's localized name
   * @return Reference to the LocaleString containing the name
   */
  const LocaleString &name() const { return name_; }

  /*
   * @brief Set the component's localized name
   * @param name The new localized name for the component
   */
  void set_name(const LocaleString &name) { name_ = name; }

  /**
   * @brief Get the component's joystick shortcut
   * @return Reference to the JoystickEvent shortcut
   */
  const JoystickEvent &shortcut() const { return shortcut_; }

  /*
   * @brief Set the component's joystick shortcut
   * @param shortcut The new joystick shortcut for the component
   */
  void set_shortcut(const JoystickEvent &shortcut) { shortcut_ = shortcut; }

  /**
   * @brief Get the component's display sequence number
   * @return The display sequence value
   */
  uint32_t display_sequence() const { return display_sequence_; };

  /*
   * @brief Set the component's display sequence number
   * @param display_sequence The new display sequence for the component
   */
  void set_display_sequence(uint32_t display_sequence) {
    display_sequence_ = display_sequence;
  }

  /**
   * @brief Cast component to specific derived type
   * @tparam T The target component type to cast to
   * @return Shared pointer to the component cast to type T, or nullptr if cast
   * fails
   *
   * This template method provides safe dynamic casting to specific component
   * types. Use this to access derived class methods after checking the
   * component type.
   */
  template <class T> std::shared_ptr<T> As() {
    return std::dynamic_pointer_cast<T>(shared_from_this());
  }

  /**
   * @brief Cast component to specific derived type (const version)
   * @tparam T The target component type to cast to
   * @return Shared pointer to the component cast to type T, or nullptr if cast
   * fails
   *
   * This template method provides safe dynamic casting to specific component
   * types. Use this to access derived class methods after checking the
   * component type.
   */
  template <class T> std::shared_ptr<const T> As() const {
    return std::dynamic_pointer_cast<const T>(shared_from_this());
  }

  /**
   * @brief Get the component's type
   * @return The ComponentType enumeration value
   */
  virtual ComponentType GetType() const { return ComponentType::kNONE; }

  /**
   * @brief Check if this component equals another component
   * @param other The other component to compare against
   * @return true if components are equal, false otherwise
   */
  virtual bool Equal(const Component &other) const;

  /**
   * @brief Create a deep copy of the component
   * @return A new ComponentPtr that is a copy of this component
   */
  virtual ComponentPtr Clone() const;

  /**
   * @brief Convert the component to a JSON representation
   * @param lang The language code for localization. If empty, all translations
   * are included. If set, only the specific translation is included. If not
   * found, the default language is used.
   * @return A JSON object representing the component
   */
  virtual json ToJson([[maybe_unused]] const std::string &lang) const;

  /**
   * @brief Execute the click callback for this component (internal method)
   * @param clicked_component The component that was clicked, carrying context
   * from the request
   * @return Optional toast message to display
   *
   * This method executes the component's click callback function.
   * It's primarily used internally by the ComponentMgr.
   */
  virtual OptionalToast OnClick(const ConstComponentPtr &clicked_component);

private:
  /// @brief Unique identifier for the component
  std::string id_;

  /// @brief Localized name of the component
  LocaleString name_;

  /// @brief Callback function to execute when component is clicked
  ComponentClickCallback click_callback_;

  /// @brief Joystick shortcut for the component
  JoystickEvent shortcut_;

  /// @brief Display sequence number for ordering
  uint32_t display_sequence_;
};

/**
 * @brief Icon-based component that displays an image
 *
 * IconComponent extends the base Component with an icon path.
 */
class IconComponent : public Component {
public:
  /**
   * @brief Construct a new Icon Component
   * @param id Unique identifier for the component
   * @param name Localized name of the component
   * @param path File system path to the icon image
   * @param click_callback Function to call when component is clicked
   * @param shortcut Optional joystick shortcut for the component
   * @param display_sequence Order in which component should be displayed
   */
  IconComponent(const std::string &id, const LocaleString &name,
                const std::string &path,
                ComponentClickCallback click_callback = click_callback_empty,
                JoystickEvent shortcut = JoystickEvent::NONE(),
                const uint32_t display_sequence = ComponentDisplaySequenceAuto);

  /**
   * @brief Virtual destructor
   */
  virtual ~IconComponent() = default;

  /**
   * @brief Get the path to the icon file
   * @return The file system path to the icon
   */
  std::string path() const { return path_; }

  /*
   * @brief Set the path to the icon file
   * @param path The new file system path to the icon
   */
  void set_path(const std::string &path) { path_ = path; }

  /**
   * @brief Get the component type
   * @return ComponentType::kICON
   */
  virtual ComponentType GetType() const override {
    return ComponentType::kICON;
  }

  /**
   * @brief Check if this component equals another component
   * @param other The other component to compare against
   * @return true if components are equal, false otherwise
   */
  virtual bool Equal(const Component &other) const override;

  /**
   * @brief Create a deep copy of the component
   * @return A new ComponentPtr that is a copy of this component
   */
  virtual ComponentPtr Clone() const;

  /**
   * @brief Convert the component to a JSON representation
   * @param lang The language code for localization. If empty, all translations
   * are included. If set, only the specific translation is included. If not
   * found, the default language is used.
   * @return A JSON object representing the component
   */
  virtual json ToJson([[maybe_unused]] const std::string &lang) const override;

protected:
  /// @brief File system path to the icon image
  std::string path_;
};

/**
 * @brief Icon component with integer state management
 *
 * StateIconComponent extends IconComponent with an integer state value
 * that can be used to represent different component states.
 */
class StateIconComponent : public IconComponent {
public:
  /**
   * @brief Construct a new State Icon Component
   * @param id Unique identifier for the component
   * @param name Localized name of the component
   * @param path File system path to the icon image
   * @param state Initial integer state value
   * @param click_callback Function to call when component is clicked
   * @param shortcut Optional joystick shortcut for the component
   * @param display_sequence Order in which component should be displayed
   */
  StateIconComponent(
      const std::string &id, const LocaleString &name, const std::string &path,
      const int state,
      ComponentClickCallback click_callback = click_callback_empty,
      JoystickEvent shortcut = JoystickEvent::NONE(),
      const uint32_t display_sequence = ComponentDisplaySequenceAuto);

  /**
   * @brief Destructor
   */
  ~StateIconComponent() = default;

  /**
   * @brief Get the current state value
   * @return The integer state value
   */
  int state() const { return state_; }

  /**
   * @brief Set the state value
   * @param state The new integer state value
   */
  void set_state(const int state) { state_ = state; }

  /**
   * @brief Get the component type
   * @return ComponentType::kSTATE_ICON
   */
  virtual ComponentType GetType() const override {
    return ComponentType::kSTATE_ICON;
  }

  /**
   * @brief Check if this component equals another component
   * @param other The other component to compare against
   * @return true if components are equal, false otherwise
   */
  virtual bool Equal(const Component &other) const override;

  /**
   * @brief Create a deep copy of the component
   * @return A new ComponentPtr that is a copy of this component
   */
  virtual ComponentPtr Clone() const;

  /**
   * @brief Convert the component to a JSON representation
   * @param lang The language code for localization. If empty, all translations
   * are included. If set, only the specific translation is included. If not
   * found, the default language is used.
   * @return A JSON object representing the component
   */
  virtual json ToJson([[maybe_unused]] const std::string &lang) const override;

protected:
  /// @brief Integer state value
  int state_;
};

/**
 * @brief Icon component with boolean state management
 *
 * DefaultStateIconComponent extends StateIconComponent but uses a boolean
 * state instead of an integer for simpler on/off type components.
 */
class DefaultStateIconComponent : public StateIconComponent {
public:
  /**
   * @brief Construct a new Default State Icon Component
   * @param id Unique identifier for the component
   * @param name Localized name of the component
   * @param path File system path to the icon image
   * @param state Initial boolean state value
   * @param click_callback Function to call when component is clicked
   * @param shortcut Optional joystick shortcut for the component
   * @param display_sequence Order in which component should be displayed
   */
  DefaultStateIconComponent(
      const std::string &id, const LocaleString &name, const std::string &path,
      const bool state,
      ComponentClickCallback click_callback = click_callback_empty,
      JoystickEvent shortcut = JoystickEvent::NONE(),
      const uint32_t display_sequence = ComponentDisplaySequenceAuto);

  /**
   * @brief Destructor
   */
  ~DefaultStateIconComponent() = default;

  /**
   * @brief Get the current boolean state
   * @return true if component is in "on" state, false otherwise
   */
  bool state() const { return state_; }

  /**
   * @brief Set the boolean state
   * @param state The new boolean state value
   */
  void set_state(const bool state) { state_ = state; }

  /**
   * @brief Get the component type
   * @return ComponentType::kDEFAULT_STATE_ICON
   */
  virtual ComponentType GetType() const override {
    return ComponentType::kDEFAULT_STATE_ICON;
  }

  /**
   * @brief Check if this component equals another component
   * @param other The other component to compare against
   * @return true if components are equal, false otherwise
   */
  virtual bool Equal(const Component &other) const override;

  /**
   * @brief Create a deep copy of the component
   * @return A new ComponentPtr that is a copy of this component
   */
  virtual ComponentPtr Clone() const;

  /**
   * @brief Convert the component to a JSON representation
   * @param lang The language code for localization. If empty, all translations
   * are included. If set, only the specific translation is included. If not
   * found, the default language is used.
   * @return A JSON object representing the component
   */
  virtual json ToJson([[maybe_unused]] const std::string &lang) const override;
};

/**
 * @brief Manager class for handling UI components
 *
 * ComponentMgr provides centralized management of all UI components including
 * adding, removing, updating components and handling component interactions.
 */
class ComponentMgr {
public:
  /**
   * @brief Construct a new Component Manager
   * @param node Pointer to the associated AgentNode
   */
  ComponentMgr(AgentNode *node);

  /**
   * @brief Destructor
   */
  ~ComponentMgr() = default;

  /**
   * @brief Get a component by its ID
   * @param id The unique identifier of the component
   * @return Shared pointer to the component, or nullptr if not found
   */
  ComponentPtr GetComponent(const std::string &id);

  /**
   * @brief Get all components
   * @return Vector containing shared pointers to all components
   */
  std::vector<ComponentPtr> GetAllComponents() const;

  /**
   * @brief Add a single component
   * @param component Shared pointer to the component to add
   */
  void AddComponent(const ComponentPtr &component);

  /**
   * @brief Add multiple components at once
   * @param components Vector of shared pointers to components to add.
   */
  template <class T,
            typename = std::enable_if_t<std::is_base_of_v<Component, T>>>
  void AddComponents(const std::vector<std::shared_ptr<T>> &components);

  /**
   * @brief Update an existing component
   * @param component Shared pointer to the updated component
   */
  void UpdateComponent(const ComponentPtr &component);

  /**
   * @brief Remove a component
   * @param component Shared pointer to the component to remove
   */
  void RemoveComponent(const ComponentPtr &component);

  /**
   * @brief Replace all components with a new set
   * @param components Vector of shared pointers to the new components
   */
  template <class T,
            typename = std::enable_if_t<std::is_base_of_v<Component, T>>>
  void ReplaceComponents(const std::vector<std::shared_ptr<T>> &components);

  /**
   * @brief Publish a toast message to all App clients
   * @param message The localized message to display
   */
  void PublishToast(LocaleString message) const;

private:
  /**
   * @brief Generate a unique sequence number for a component
   * @param component The component for which to generate the sequence number
   */
  void GenerateComponentSequence(const ComponentPtr &component);

  /**
   * @brief Handle a component click event (internal method)
   * @param clicked_component The clicked component, carrying context from the
   * request
   * @return Optional toast message to display
   *
   * This method is called internally by the service callback handlers
   * and is not intended for direct external use.
   */
  OptionalToast OnComponentClick(const ConstComponentPtr &clicked_component);

  /**
   * @brief Handle joystick events and trigger appropriate component actions
   * (internal method)
   * @param joystick_event The joystick event to process
   * @return true if event was handled successfully, false otherwise
   *
   * This method is called internally by the AgentNode joystick callback
   * and is not intended for direct external use.
   */
  bool OnJoystickEvent(const JoystickEvent &joystick_event);

  /**
   * @brief Publish current component list to subscribers (internal method)
   * @param component The component to publish, if null will publish all
   * components
   *
   * This method handles the internal protocol message generation and
   * publishing.
   */
  void PublishComponents(const ComponentPtr &component) const;

  /**
   * @brief Generate protocol message JSON for a component or all components
   * @param component The component to generate message for, if null will
   * generate for all components
   * @param lang The language code for localization. If empty, all translations
   * are included. If set, only the specific translation is included. If not
   * found, the default language is used.
   * @return JSON string representing the protocol message
   */
  json GenerateProtocolMessage(const ComponentPtr &component,
                               const std::string &lang = "") const;

  /**
   * @brief Generate protocol message JSON for a toast message
   * @param message The toast message to generate protocol message for
   * @param lang The language code for localization. If empty, all translations
   * are included. If set, only the specific translation is included. If not
   * found, the default language is used.
   * @return JSON string representing the protocol message
   */
  json GenerateProtocolMessageToast(const LocaleString &message,
                                    const std::string &lang = "") const;

private:
  /// @brief Pointer to the associated AgentNode
  AgentNode *node_ = nullptr;

  /// @brief Mutex for thread-safe component access
  mutable std::mutex mutex_;

  /// @brief Map of component IDs to component objects
  std::unordered_map<std::string, ComponentPtr> components_;

  /// @brief Atomic counter for generating unique component IDs
  std::atomic<int> auto_display_sequence_index_{0x10000};

  /// @brief Grant AgentNode access to private methods for event handling
  friend class AgentNode;
};

} // end of namespace booster_agent_framework