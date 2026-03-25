#!/bin/bash

usage() {
    echo "Usage: $0 <AGENT_PATH> <USER>@<HOST> or $0 <AGENT_IMAGE_PATH> <USER>@<HOST>"
    echo "Example 1 (directory, remotely): $0 ./examples booster@192.168.100.2"
    echo "Example 2 (file, remotely): $0 ./com_boosterobotics_examples_1.0.0.appimage booster@192.168.100.2"
    echo "Example 3 (directory, locally): $0 ./examples"
    exit 0
}

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    key="$1"
    case $key in
        -h|--help)
            usage
            ;;
        -*)
            echo "Error: Unknown option $key"
            exit 1
            ;;
        *)
            # Positional arguments
            if [ -z "$AGENT_PATH" ]; then
                AGENT_PATH="$1"
            else
                TARGET_PATH="$1"
            fi
            shift
            ;;
    esac
done

# Validate required parameters
if [ -z "$AGENT_PATH" ]; then
    echo "Error: AGENT_PATH is required"
    usage
    exit 1
fi

#Resolve User and server from target server
# if TARGET_PATH is empty, set it to CURRENT_USER@localhost
if [ -z "$TARGET_PATH" ]; then
    TARGET_PATH="$USER@localhost"
    TARGET_USER="$USER"
    TARGET_SERVER="localhost"
elif [[ "$TARGET_PATH" == *"@"* ]]; then
    TARGET_USER=$(echo "$TARGET_PATH" | cut -d'@' -f1)
    TARGET_SERVER=$(echo "$TARGET_PATH" | cut -d'@' -f2)
else
    echo "Error: TARGET_PATH must be in the format <USER>@<HOST>"
    usage
    exit 1
fi

# Set default target server to localhost if not provided
TARGET_SERVER=${TARGET_SERVER:-127.0.0.1}
TEMP_INSTALL_DIR="/tmp"
INSTALL_AGENT_SCRIPT_PATH="/opt/booster/BoosterAgent/install_agent_client"

# Function to validate and copy AppImage
deploy_appimage() {
    local local_path="$1"
    local filename=$(basename "$local_path")

    # Validate file exists
    if [ ! -f "$local_path" ]; then
        echo "Error: AppImage file not found - $local_path"
        exit 1
    fi

    # Validate file is an AppImage
    if [[ "$filename" != *.AppImage ]]; then
        echo "Error: File is not an AppImage - $filename"
        exit 1
    fi

    if [ "$TARGET_SERVER" = "127.0.0.1" ] || [ "$TARGET_SERVER" = "localhost" ]; then
        echo "Deploying locally to $TEMP_INSTALL_DIR"
        # Create local directory if it doesn't exist
        # mkdir -p "$TEMP_INSTALL_DIR" || { echo "Error: Failed to create local directory $TEMP_INSTALL_DIR"; exit 1; }
        # Copy file locally
        cp "$local_path" "$TEMP_INSTALL_DIR/" || { echo "Error: Failed to copy file to local directory"; exit 1; }
        echo "Calling install script locally"
        $INSTALL_AGENT_SCRIPT_PATH $TEMP_INSTALL_DIR/$filename || { echo "Error: Failed to execute install script locally"; exit 1; }
    else
        echo "Deploying to remote server $TARGET_SERVER:$TEMP_INSTALL_DIR"
        # Use scp for remote deployment
        scp "$local_path" "$TARGET_USER@$TARGET_SERVER:$TEMP_INSTALL_DIR/" || { echo "Error: Failed to copy file to remote server"; exit 1; }
        echo "Calling install script on remote server $TARGET_SERVER"
        ssh "$TARGET_USER@$TARGET_SERVER" "$INSTALL_AGENT_SCRIPT_PATH $TEMP_INSTALL_DIR/$filename" || { echo "Error: Failed to execute install script on remote server"; exit 1; }
    fi
    echo "Successfully deployed $filename"
}

# Main execution
AGENT_IMAGE_FILE=""
if [ -d "$AGENT_PATH" ]; then
    AGENT_DIR="$(cd $AGENT_PATH && pwd)"
    AGENT_JSON="$AGENT_DIR/agent.json"
    if [ ! -f "$AGENT_JSON" ]; then
        echo -e "${RED}ERROR in line $LINENO: $AGENT_JSON does not exist${NC}"
        exit 1
    fi

    # Validate JSON fields and types
    REQUIRED_KEYS=(id version app_image)
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
    if ! jq -e '.version | strings' "$AGENT_JSON" &>/dev/null; then
        echo -e "${RED}ERROR in line $LINENO: agent.json field 'version' must be a string${NC}"
        exit 1
    fi

    AGENT_ID=$(jq -r .id "$AGENT_JSON")
    AGENT_VERSION=$(jq -r .version "$AGENT_JSON")

    APPIMAGE_OUTPUT_DIR="$AGENT_DIR/dist"
    AGENT_IMAGE_FILE="$APPIMAGE_OUTPUT_DIR/$AGENT_ID-$AGENT_VERSION.AppImage"
    echo "Deploying AppImage: $AGENT_IMAGE_FILE"
    deploy_appimage "$AGENT_IMAGE_FILE"
elif [ -f "$AGENT_PATH" ]; then
    AGENT_IMAGE_FILE="$AGENT_PATH"
    deploy_appimage "$AGENT_IMAGE_FILE"
else
    echo "Error: AGENT_PATH must be a valid directory or file - $AGENT_PATH"
    exit 1
fi