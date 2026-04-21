#!/bin/bash

set -e

# Color definitions
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Check arguments
if [ $# -lt 1 ]; then
    echo -e "${RED}ERROR in line $LINENO: Usage: $0 AGENT_DIR${NC}"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOL_BIN_DIR="$SCRIPT_DIR/bin"
# Set source directories (update paths if different in your project)
SOURCE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
NODE_SRC="$SOURCE_DIR/node"
PROTOCOL_SRC="$SOURCE_DIR/protocol"

# Verify source directories exist
if [ ! -d "$NODE_SRC" ] || [ ! -d "$PROTOCOL_SRC" ]; then
    echo -e "${RED}Error: Source directories (node and protocol) not found!${NC}" >&2
    exit 1
fi

# Check architecture
ARCHSTR=$(uname -m)
# Check ARCH, must be aarch64 or x86_64
if [ "$ARCHSTR" != "aarch64" ] && [ "$ARCHSTR" != "x86_64" ]; then
    echo "Error: ARCH must be aarch64 or x86_64, get $ARCHSTR, not supported yet"
    exit 1
else
    echo "ARCH is supported: $ARCHSTR"
fi

AGENT_DIR_RELATIVE=""
COLCON_EXTRA_ARGS=()
# Parameter parsing to examine and filter all input arguments
# Parameter parsing loop
while [[ $# -gt 0 ]]; do
    case "$1" in
        # Help option
        -h|--help)
            echo "Usage: $0 [OPTIONS] AGENT_DIR"
            echo "Required parameters:"
            echo "  AGENT_DIR           Target directory for the agent (no prefix)"
            echo "Optional flags:"
            echo "  -h, --help          Show this help message"
            echo "Colcon flags:"
            echo "  --symlink-install   colcon param --symlink-install"
            exit 0
            ;;
        # End of script arguments, remaining go to colcon
        --*)
            COLCON_EXTRA_ARGS+=("$1")
            shift
            COLCON_EXTRA_ARGS+=("$@")
            break
            ;;
        # Unknown flag
        -*) 
            echo "Error: Unknown parameter '$1'" >&2
            echo "Use -h or --help to see valid options" >&2
            exit 1
            ;;
        # Positional parameter (AGENT_DIR)
        *)
            if [[ -z "$AGENT_DIR_RELATIVE" ]]; then
                AGENT_DIR_RELATIVE="$1"
                shift
            else
                echo "Error: Unexpected extra parameter '$1'" >&2
                echo "Only one positional parameter (AGENT_DIR) is allowed" >&2
                exit 1
            fi
            ;;
    esac
done

AGENT_DIR="$(cd "$(dirname "$AGENT_DIR_RELATIVE")" && pwd)/$(basename "$AGENT_DIR_RELATIVE")"

# Process --base-paths argument
new_args=()
found=0
i=0
while [ $i -lt ${#COLCON_EXTRA_ARGS[@]} ]; do
    arg="${COLCON_EXTRA_ARGS[$i]}"
    if [[ $arg == --base-paths* ]]; then
        found=1
        if [[ $arg == --base-paths=* ]]; then
            # Handle --base-paths=path1,path2 format
            path_value="${arg#--base-paths=}"
            new_path_value="${PROTOCOL_SRC},${NODE_SRC},${AGENT_DIR}/*,${path_value}"
            new_args+=("--base-paths=${new_path_value}")
            i=$((i + 1))
        else
            # Handle --base-paths path1 path2 format
            paths=()
            i=$((i + 1))
            # Collect existing paths until next flag or end of array
            while [ $i -lt ${#COLCON_EXTRA_ARGS[@]} ] && [[ "${COLCON_EXTRA_ARGS[$i]}" != --* ]]; do
                # Convert relative path to absolute path if needed
                path_arg="${COLCON_EXTRA_ARGS[$i]}"
                if [[ $path_arg == ./* ]]; then
                    # Convert relative path to absolute
                    abs_path="$(cd "$(dirname "$path_arg")" && pwd)/$(basename "$path_arg")"
                    paths+=("$abs_path")
                else
                    paths+=("$path_arg")
                fi
                i=$((i + 1))
            done
            # Append required paths first, then user-specified paths
            new_args+=("--base-paths")
            new_args+=("${PROTOCOL_SRC}")
            new_args+=("${NODE_SRC}")
            new_args+=("${AGENT_DIR}/*")
            new_args+=("${paths[@]}")
        fi
    else
        new_args+=("$arg")
        i=$((i + 1))
    fi
done

# Add --base-paths if not found
if [ $found -eq 0 ]; then
    new_args+=("--base-paths")
    new_args+=("${PROTOCOL_SRC}")
    new_args+=("${NODE_SRC}")
    new_args+=("${AGENT_DIR}/*")
fi

COLCON_EXTRA_ARGS=("${new_args[@]}")

# 2. Check directory structure
if [ ! -d "$AGENT_DIR" ]; then
    echo -e "${RED}ERROR in line $LINENO: target agent dir '$AGENT_DIR_RELATIVE' does not exist${NC}"
    exit 1
fi
if [ ! -d "$AGENT_DIR/res" ]; then
    echo -e "${RED}ERROR in line $LINENO: $AGENT_DIR/res does not exist${NC}"
    exit 1
fi
if [ ! -d "$AGENT_DIR/ros2_main_pkg" ]; then
    echo -e "${RED}ERROR in line $LINENO: $AGENT_DIR/ros2_main_pkg does not exist${NC}"
    exit 1
fi

# 3. Check and validate agent.json
AGENT_RES_DIR="$AGENT_DIR/res"
AGENT_JSON="$AGENT_DIR/agent.json"
if [ ! -f "$AGENT_JSON" ]; then
    echo -e "${RED}ERROR in line $LINENO: $AGENT_JSON does not exist${NC}"
    exit 1
fi

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}WARN in line $LINENO: Please install jq: sudo apt install jq${NC}"
    exit 1
fi

# Check if colcon is installed
if ! command -v colcon &> /dev/null; then
    echo -e "${YELLOW}WARN in line $LINENO: Please install ros2 humble dev tools: refer to https://docs.ros.org/en/humble/Installation.html${NC}"
    exit 1
fi

# Check if libfuse2 is installed
if ! command -v fusermount &> /dev/null; then
    echo -e "${YELLOW}WARN in line $LINENO: Please install libfuse2: sudo apt install libfuse2${NC}"
    exit 1
fi

# Validate JSON fields and types
REQUIRED_KEYS=(id name version description gait app_image)
for key in "${REQUIRED_KEYS[@]}"; do
    if ! jq -e ".${key}" "$AGENT_JSON" &>/dev/null; then
        echo -e "${RED}ERROR in line $LINENO: agent.json missing field: $key${NC}"
        exit 1
    fi
done

# Type checks
if ! jq -e '.id | strings' "$AGENT_JSON" &>/dev/null; then
    echo -e "${RED}ERROR in line $LINENO: agent.json field 'id' must be a string${NC}"
    exit 1
fi
if ! jq -e '.name | strings' "$AGENT_JSON" &>/dev/null; then
    echo -e "${RED}ERROR in line $LINENO: agent.json field 'name' must be a string${NC}"
    exit 1
fi
if ! jq -e '.version | strings' "$AGENT_JSON" &>/dev/null; then
    echo -e "${RED}ERROR in line $LINENO: agent.json field 'version' must be a string${NC}"
    exit 1
fi
if ! jq -e '.description | strings' "$AGENT_JSON" &>/dev/null; then
    echo -e "${RED}ERROR in line $LINENO: agent.json field 'description' must be a string${NC}"
    exit 1
fi
if ! jq -e '.gait | strings' "$AGENT_JSON" &>/dev/null; then
    echo -e "${RED}ERROR in line $LINENO: agent.json field 'gait' must be a string${NC}"
    exit 1
fi
if ! jq -e '.app_image | objects' "$AGENT_JSON" &>/dev/null; then
    echo -e "${RED}ERROR in line $LINENO: agent.json field 'app_image' must be an object${NC}"
    exit 1
fi
if ! jq -e '.ros2 | objects' "$AGENT_JSON" &>/dev/null; then
    echo -e "${RED}ERROR in line $LINENO: agent.json field 'ros2' must be an object${NC}"
    exit 1
fi
if ! jq -e '.ros2.package_name | strings' "$AGENT_JSON" &>/dev/null; then
    echo -e "${RED}ERROR in line $LINENO: agent.json field 'ros2.package_name' must be a string${NC}"
    exit 1
fi
if ! jq -e '.ros2.launch_file | strings' "$AGENT_JSON" &>/dev/null; then
    echo -e "${RED}ERROR in line $LINENO: agent.json field 'ros2.launch_file' must be a string${NC}"
    exit 1
fi

VALID_SHORTCUTS=("LT+RT+UP" "LT+RT+DOWN" "LT+RT+LEFT" "LT+RT+RIGHT" "LT+RT+Y" "LT+RT+A" "LT+RT+B")
VALID_SHORTCUTS_JSON=$(printf '%s\n' "${VALID_SHORTCUTS[@]}" | jq -R . | jq -s .)
if jq -e --argjson valid "$VALID_SHORTCUTS_JSON" \
   '.shortcut | select(. != null and . != "") | IN($valid[]) | not' \
   "$AGENT_JSON" &>/dev/null; then
    echo -e "${RED}ERROR in line $LINENO: agent.json field 'shortcut' must be a string or valid ${NC}"
    exit 1
fi

validate_array_field() {
    local field_name="$1"
    local jq_output
    local all_value_valid=true    
    if jq -e ".requirements | has(\"$field_name\")" "$AGENT_JSON" &>/dev/null; then
        jq_output=$(jq -e "(.requirements.$field_name | type == \"array\") and (.requirements.$field_name[] | type == \"string\")" "$AGENT_JSON" | grep false || true)
        if [ -z "$jq_output" ]; then
            all_value_valid=true
        else
            for value in $jq_output; do
                if [ "$value" == "false" ]; then
                    all_value_valid=false
                    break
                fi
            done
        fi
        if ! $all_value_valid &>/dev/null; then
            echo -e "${RED}ERROR in line $LINENO: agent.json field'requirements.$field_name' must be a string array${NC}"
            exit 1
        fi
    fi
}

if jq -e 'has("requirements")' "$AGENT_JSON" &>/dev/null; then
    if ! jq -e '.requirements | objects' "$AGENT_JSON" &>/dev/null; then
        echo -e "${RED}ERROR in line $LINENO: agent.json field 'requirements' must be an object${NC}"
        exit 1
    fi
    validate_array_field models
    validate_array_field nvidia_jetpack_main_versions
fi

# Check app_image.icon exists, is a string
ICON_PATH=$(jq -r '.app_image.icon' "$AGENT_JSON")
if [ -z "$ICON_PATH" ] || [ "$ICON_PATH" = "null" ]; then
    echo -e "${YELLOW}WARN in line $LINENO: agent.json field 'app_image.icon' should be set and non-empty${NC}"
fi
if ! jq -e '.app_image.icon | strings' "$AGENT_JSON" &>/dev/null; then
    echo -e "${RED}ERROR in line $LINENO: agent.json field 'app_image.icon' must be a string${NC}"
    exit 1
fi
# Check if icon file exists
if [ ! -f "$AGENT_DIR/$ICON_PATH" ]; then
    echo -e "${RED}ERROR in line $LINENO: Icon file $ICON_PATH does not exist${NC}"
    exit 1
fi

# 4. Build ros2
BUILD_ROS2="$AGENT_DIR/build_ros2"
mkdir -p "$BUILD_ROS2" || exit -1 
echo "Call colcon to build target, cmd:"
echo "colcon --log-base $BUILD_ROS2/log build --build-base $BUILD_ROS2/build --install-base $BUILD_ROS2/install ${COLCON_EXTRA_ARGS[@]}"
colcon --log-base "$BUILD_ROS2/log" build --build-base "$BUILD_ROS2/build" --install-base "$BUILD_ROS2/install" "${COLCON_EXTRA_ARGS[@]}" || exit -1 

# 5. Build AppImage directory and files
BUILD_IMAGE="$AGENT_DIR/build_image"
mkdir -p "$BUILD_IMAGE/bin" || exit -1 

# Copy components
cp -f "$TOOL_BIN_DIR/start" "$BUILD_IMAGE/bin/" || exit -1 
cp -f "$TOOL_BIN_DIR/stop" "$BUILD_IMAGE/bin/" || exit -1 
cp -f "$TOOL_BIN_DIR/AppRun" "$BUILD_IMAGE/" || exit -1 

# Generate agent.desktop
AGENT_ID=$(jq -r .id "$AGENT_JSON")
AGENT_NAME=$(jq -r .name "$AGENT_JSON")
AGENT_VERSION=$(jq -r .version "$AGENT_JSON")
AGENT_DESCRIPTION=$(jq -r .description "$AGENT_JSON")
AGENT_ICON_PATH=$(jq -r .app_image.icon "$AGENT_JSON")
AGENT_ICON="${AGENT_ICON_PATH%.*}"

cat > "$BUILD_IMAGE/agent.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=$AGENT_ID
Comment=$AGENT_DESCRIPTION
Exec=AppRun
Icon=$AGENT_ICON
Terminal=true
Categories=Utility;
EOF

# Copy all resources files and agent.json to $BUILD_IMAGE
echo "copy resource files and agent.json to $BUILD_IMAGE/"
mkdir -p "$BUILD_IMAGE/res" || exit -1
cp -rf $AGENT_RES_DIR/* $BUILD_IMAGE/res || exit -1
cp -f $AGENT_JSON $BUILD_IMAGE/ || exit -1

# Copy build_ros2 to $BUILD_IMAGE
mkdir -p $BUILD_IMAGE/agent || exit -1
rm -rf $BUILD_IMAGE/agent/* || exit -1
cp -r $BUILD_ROS2/install/* $BUILD_IMAGE/agent/ || exit -1
echo 'copy build_ros2 output to $BUILD_IMAGE/agent successfully'

# 6. Package AppImage
APPIMAGE_OUTPUT_DIR="$AGENT_DIR/dist"
mkdir -p $APPIMAGE_OUTPUT_DIR || exit -1
# if ARCHSTR is aarch64, set ARCH to arm_aarch64
if [ "$ARCHSTR" = "aarch64" ]; then
    export ARCH="arm_aarch64"
else
    export ARCH=$ARCHSTR
fi
$TOOL_BIN_DIR/appimagetool_${ARCHSTR} $BUILD_IMAGE $APPIMAGE_OUTPUT_DIR/$AGENT_ID-$AGENT_VERSION.AppImage || exit 1

echo "Build complete: $APPIMAGE_OUTPUT_DIR/$AGENT_ID-$AGENT_VERSION.AppImage"