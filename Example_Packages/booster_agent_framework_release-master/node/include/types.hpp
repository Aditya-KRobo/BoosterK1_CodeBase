/**
 * @file types.hpp
 * @brief Common type definitions and utilities for Booster agent framework
 * @author Booster Robotics
 * @date 2025
 */

#pragma once
#include <cstring>
#include <iostream>
#include <json.hpp>
#include <optional>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>

namespace booster_agent_framework {

using json = nlohmann::json;

/// @brief Current API level of the agent framework
constexpr const uint32_t kAgentFrameworkApiLevel = 1;

/// @brief Default lang for LocaleString
constexpr const char *kDefaultLang = "en";

/**
 * @brief Internationalization support for text strings
 *
 * LocaleString provides a way to store text in multiple languages
 * and retrieve the appropriate translation based on locale.
 */
class LocaleString {
public:
  /**
   * @brief Construct LocaleString with default language text
   * @param default_string The text in the default language
   * @throws std::invalid_argument if default_lang is not supported
   */
  LocaleString(const std::string &default_string);

  /**
   * @brief Construct LocaleString with multiple language _translations
   * @param init_list Initializer list of language-text pairs
   * @throws std::invalid_argument if any language is unsupported or
   * default_lang not in list
   */
  LocaleString(std::initializer_list<std::pair<const std::string, std::string>>
                   init_list);

  /**
   * @brief Construct LocaleString with English and Chinese translations
   * @param en_str The text in English
   * @param zh_str The text in Chinese
   * @throws std::invalid_argument if default_lang is not supported
   */
  LocaleString(const std::string &en_str, const std::string &zh_str);

  /**
   * @brief Add or update a translation for a language
   * @param lang The language code
   * @param str The translated text
   * @throws std::invalid_argument if language is not supported
   */
  void AddTranslation(const std::string &lang, const std::string &str);

  /**
   * @brief Get the localized string for a specific language
   * @param lang The requested language code
   * @return The text in the requested language, or default language if not
   * available
   */
  std::string GetString(const std::string &lang) const;

  /**
   * @brief Convert the LocaleString to JSON
   * @param lang The language code to use. If empty, all translations are
   * included. If set, only the specific translation is included. If not found,
   * the default language is used.
   * @return A JSON object representing the LocaleString
   */
  json ToJson(const std::string &lang = "") const;

private:
  /**
   * @brief Check if a locale is supported
   * @param locale The locale string to validate
   * @return true if locale is supported, false otherwise
   */
  bool IsValidLocale(const char *locale) const {
    return supported_langs_.find(locale) != supported_langs_.end();
  }

private:
  /// @brief Set of supported language codes
  inline static std::unordered_set<std::string> supported_langs_ = {"en", "zh"};

  /// @brief Map of language codes to translated strings
  std::unordered_map<std::string, std::string> translations_;
};

/**
 * @brief Sanitize a string by replacing illegal characters for ROS2 framework
 * @param str The string to sanitize
 * @return The sanitized string with '.' replaced by '_'
 *
 * This function ensures string compatibility with ROS2 naming conventions
 * by replacing problematic characters like dots with underscores.
 */
std::string SanitizeString(const std::string &str);

} // namespace booster_agent_framework