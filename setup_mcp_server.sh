#!/bin/bash
# Enhanced setup script for hestai-mcp server with automatic Claude Desktop configuration

set -euo pipefail

# Colors for output
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly RED='\033[0;31m'
readonly NC='\033[0m' # No Color

# Configuration
readonly VENV_PATH=".venv"
readonly DESKTOP_CONFIG_FLAG=".desktop_configured"

# Print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1" >&2
}

print_warning() {
    echo -e "${YELLOW}!${NC} $1"
}

print_info() {
    echo -e "${YELLOW}$1${NC}"
}

# Get the script's directory (works on all platforms)
get_script_dir() {
    cd "$(dirname "$0")" && pwd
}

# Detect the operating system
detect_os() {
    case "$OSTYPE" in
        darwin*)  echo "macos" ;;
        linux*)
            if grep -qi microsoft /proc/version 2>/dev/null; then
                echo "wsl"
            else
                echo "linux"
            fi
            ;;
        msys*|cygwin*|win32) echo "windows" ;;
        *)        echo "unknown" ;;
    esac
}

# Get Claude config path based on platform
get_claude_config_path() {
    local os_type=$(detect_os)

    case "$os_type" in
        macos)
            echo "$HOME/Library/Application Support/Claude/claude_desktop_config.json"
            ;;
        linux)
            echo "$HOME/.config/Claude/claude_desktop_config.json"
            ;;
        wsl)
            local win_appdata
            if command -v wslvar &> /dev/null; then
                win_appdata=$(wslvar APPDATA 2>/dev/null)
            fi

            if [[ -n "$win_appdata" ]]; then
                echo "$(wslpath "$win_appdata")/Claude/claude_desktop_config.json"
            else
                echo "/mnt/c/Users/$USER/AppData/Roaming/Claude/claude_desktop_config.json"
            fi
            ;;
        windows)
            echo "$APPDATA/Claude/claude_desktop_config.json"
            ;;
        *)
            echo ""
            ;;
    esac
}

# Check and update Claude Desktop configuration
update_claude_desktop_config() {
    local python_cmd="$1"
    local server_args="$2"

    # Skip if already configured
    if [[ -f "$DESKTOP_CONFIG_FLAG" ]]; then
        return 0
    fi

    local config_path=$(get_claude_config_path)
    if [[ -z "$config_path" ]]; then
        print_warning "Unable to determine Claude Desktop config path for this platform"
        return 0
    fi

    echo ""
    read -p "Automatically update Claude Desktop configuration? (Y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_info "Skipping automatic Claude Desktop configuration"
        return 0
    fi

    # Create config directory if it doesn't exist
    local config_dir=$(dirname "$config_path")
    mkdir -p "$config_dir" 2>/dev/null || true

    # Update configuration using Python for proper JSON handling
    if [[ -f "$config_path" ]]; then
        print_info "Updating existing Claude Desktop config..."
        # Create backup
        cp "$config_path" "${config_path}.backup_$(date +%Y%m%d_%H%M%S)"

        local temp_file=$(mktemp)
        python3 -c "
import json
import sys

try:
    with open('$config_path', 'r') as f:
        config = json.load(f)
except:
    config = {}

# Ensure mcpServers exists
if 'mcpServers' not in config:
    config['mcpServers'] = {}

# Add or update hestai-mcp server
config['mcpServers']['hestai-mcp'] = {
    'command': '$python_cmd',
    'args': $server_args
}

with open('$temp_file', 'w') as f:
    json.dump(config, f, indent=2)
" && mv "$temp_file" "$config_path"

    else
        print_info "Creating new Claude Desktop config..."
        cat > "$config_path" << EOF
{
  "mcpServers": {
    "hestai-mcp": {
      "command": "$python_cmd",
      "args": $server_args
    }
  }
}
EOF
    fi

    if [[ $? -eq 0 ]]; then
        print_success "Successfully updated Claude Desktop configuration"
        echo "  Config: $config_path"
        echo "  ${YELLOW}Please restart Claude Desktop to enable the MCP server${NC}"
        touch "$DESKTOP_CONFIG_FLAG"
    else
        print_error "Failed to update Claude Desktop config automatically"
        return 1
    fi
}

# Main setup
main() {
    echo "🤖 Setting up hestai-mcp server..."
    echo ""

    # Get script directory
    local script_dir=$(get_script_dir)

    # Create virtual environment if it doesn't exist
    if [ ! -d "$VENV_PATH" ]; then
        print_info "Creating Python virtual environment..."
        python3 -m venv "$VENV_PATH"
        print_success "Virtual environment created"
    fi

    # Activate virtual environment
    source "$VENV_PATH/bin/activate"

    # Install dependencies
    print_info "Installing dependencies..."
    if pip install -q -e .; then
        print_success "Dependencies installed"
    else
        print_error "Failed to install dependencies"
        exit 1
    fi

    # Get absolute paths for MCP registration
    local abs_python="$script_dir/$VENV_PATH/bin/python"
    local server_args='["-m", "hestai_mcp.mcp.server"]'

    print_success "Setup complete!"
    echo ""

    # Attempt automatic Claude Desktop configuration
    update_claude_desktop_config "$abs_python" "$server_args"

    # Show manual instructions if needed
    if [[ ! -f "$DESKTOP_CONFIG_FLAG" ]]; then
        echo ""
        print_info "Manual Configuration Instructions:"
        echo ""
        echo "To register this MCP server with Claude Desktop:"
        echo "1. Open Claude Desktop settings"
        echo "2. Go to Developer > Edit Config"
        echo "3. Add the following to 'mcpServers':"
        echo ""
        cat << EOF
  "hestai-mcp": {
    "command": "$abs_python",
    "args": [
      "-m",
      "hestai_mcp.mcp.server"
    ]
  }
EOF
        echo ""
        echo "4. Restart Claude Desktop"
    fi

    echo ""
    print_info "Available tools:"
    echo "  • clock_in: Register agent session start"
    echo "  • clock_out: Archive agent session"
    echo "  • document_submit: Submit documents (TODO - Phase 3)"
    echo ""

    # Show how to test the server
    print_info "To test the server manually:"
    echo "  source $VENV_PATH/bin/activate"
    echo "  python -m hestai_mcp.mcp.server"
    echo ""

    print_success "Happy coding! 🎉"
}

# Run main function
main "$@"
