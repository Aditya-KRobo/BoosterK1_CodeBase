/**
 * @file types.cpp
 * @brief Implementation of common types for Booster agent framework
 * @author Booster Robotics
 * @date 2025
 */

#include "types.hpp"
#include <algorithm>

namespace booster_agent_framework {

// Implementations moved from header (multi-line functions)

LocaleString::LocaleString(const std::string &default_string) {
  translations_[kDefaultLang] = default_string;
}

LocaleString::LocaleString(
    std::initializer_list<std::pair<const std::string, std::string>>
        init_list) {
  for (const auto &pair : init_list) {
    if (!IsValidLocale(pair.first.c_str())) {
      throw std::invalid_argument("Locale not supported");
    }
    translations_[pair.first] = pair.second;
  }
  if (translations_.find(kDefaultLang) == translations_.end()) {
    throw std::invalid_argument(
        "Default language must be included in the initializer list.");
  }
}

LocaleString::LocaleString(const std::string &en_str, const std::string &zh_str)
    : LocaleString({{"en", en_str}, {"zh", zh_str}}) {}

void LocaleString::AddTranslation(const std::string &lang,
                                  const std::string &str) {
  if (!IsValidLocale(lang.c_str())) {
    throw std::invalid_argument("Locale not supported");
  }
  translations_[lang] = str;
}

std::string LocaleString::GetString(const std::string &lang) const {
  auto it = translations_.find(lang);
  if (it != translations_.end()) {
    return it->second;
  }
  return translations_.at(kDefaultLang); // Fallback to default language
}

json LocaleString::ToJson(const std::string &lang) const {
  json j;
  if (!lang.empty()) {
    if (translations_.find(lang) != translations_.end()) {
      j[lang] = translations_.at(lang);
    } else {
      j[kDefaultLang] = translations_.at(kDefaultLang);
    }
  } else {
    for (const auto &pair : translations_) {
      j[pair.first] = pair.second;
    }
  }
  return j;
}

std::string SanitizeString(const std::string &str) {
  std::string safe_str = str;
  std::replace(safe_str.begin(), safe_str.end(), '.', '_');
  return safe_str;
}

} // namespace booster_agent_framework