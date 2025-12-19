#!/bin/bash
# Setup script for local hestai-mcp server

echo "Setting up hestai-mcp server..."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -e .

echo "✅ Setup complete!"
echo ""
echo "To register this MCP server with Claude Desktop:"
echo "1. Open Claude Desktop settings"
echo "2. Go to Developer > Edit Config"
echo "3. Add the following to 'mcpServers':"
echo ""
cat << 'EOF'
  "hestai-mcp": {
    "command": "/Volumes/HestAI-MCP/worktrees/document-submit/.venv/bin/python",
    "args": [
      "-m",
      "hestai_mcp.mcp.server"
    ]
  }
EOF
echo ""
echo "4. Restart Claude Desktop"
echo ""
echo "Available tools:"
echo "  - clock_in: Register agent session start"
echo "  - clock_out: Archive agent session"
echo "  - document_submit: (TODO - Phase 3)"
