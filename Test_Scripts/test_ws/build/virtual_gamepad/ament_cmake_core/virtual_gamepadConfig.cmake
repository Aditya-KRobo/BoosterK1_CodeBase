# generated from ament/cmake/core/templates/nameConfig.cmake.in

# prevent multiple inclusion
if(_virtual_gamepad_CONFIG_INCLUDED)
  # ensure to keep the found flag the same
  if(NOT DEFINED virtual_gamepad_FOUND)
    # explicitly set it to FALSE, otherwise CMake will set it to TRUE
    set(virtual_gamepad_FOUND FALSE)
  elseif(NOT virtual_gamepad_FOUND)
    # use separate condition to avoid uninitialized variable warning
    set(virtual_gamepad_FOUND FALSE)
  endif()
  return()
endif()
set(_virtual_gamepad_CONFIG_INCLUDED TRUE)

# output package information
if(NOT virtual_gamepad_FIND_QUIETLY)
  message(STATUS "Found virtual_gamepad: 0.0.0 (${virtual_gamepad_DIR})")
endif()

# warn when using a deprecated package
if(NOT "" STREQUAL "")
  set(_msg "Package 'virtual_gamepad' is deprecated")
  # append custom deprecation text if available
  if(NOT "" STREQUAL "TRUE")
    set(_msg "${_msg} ()")
  endif()
  # optionally quiet the deprecation message
  if(NOT ${virtual_gamepad_DEPRECATED_QUIET})
    message(DEPRECATION "${_msg}")
  endif()
endif()

# flag package as ament-based to distinguish it after being find_package()-ed
set(virtual_gamepad_FOUND_AMENT_PACKAGE TRUE)

# include all config extra files
set(_extras "")
foreach(_extra ${_extras})
  include("${virtual_gamepad_DIR}/${_extra}")
endforeach()
