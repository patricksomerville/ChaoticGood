#!/bin/bash

# Boulevard Deployment Script
echo "🌅 Deploying Boulevard to your system..."

# Set up colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Ensure Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is required but not found. Please install Python 3 first.${NC}"
    exit 1
fi

# Create a temporary directory for deployment
TEMP_DIR=$(mktemp -d)
echo -e "${BLUE}Creating temporary directory for deployment...${NC}"

# Function to clean up on exit
cleanup() {
    echo -e "${BLUE}Cleaning up temporary files...${NC}"
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

# Copy all files to temporary directory
echo -e "${BLUE}Copying Boulevard files...${NC}"
cp -r * "$TEMP_DIR/"

# Create Boulevard directory in home folder
BOULEVARD_HOME="$HOME/boulevard"
echo -e "${BLUE}Creating Boulevard directory at $BOULEVARD_HOME...${NC}"
mkdir -p "$BOULEVARD_HOME"

# Move files to Boulevard directory
echo -e "${BLUE}Moving files to Boulevard directory...${NC}"
cp -r "$TEMP_DIR"/* "$BOULEVARD_HOME/"

# Make scripts executable
chmod +x "$BOULEVARD_HOME/install.py"
chmod +x "$BOULEVARD_HOME/deploy.sh"

# Create virtual environment
echo -e "${BLUE}Creating Python virtual environment...${NC}"
cd "$BOULEVARD_HOME"
python3 -m venv venv || {
    echo -e "${RED}Failed to create virtual environment. Installing venv...${NC}"
    python3 -m pip install --user virtualenv
    python3 -m venv venv
}

# Activate virtual environment and install dependencies
echo -e "${BLUE}Activating virtual environment and installing dependencies...${NC}"
source venv/bin/activate || {
    echo -e "${RED}Failed to activate virtual environment.${NC}"
    exit 1
}

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt || {
    echo -e "${RED}Failed to install dependencies.${NC}"
    exit 1
}

# Create Boulevard command
BOULEVARD_CMD="$BOULEVARD_HOME/boulevard"
echo -e "${BLUE}Creating Boulevard command...${NC}"
cat > "$BOULEVARD_CMD" << EOL
#!/bin/bash
source "$BOULEVARD_HOME/venv/bin/activate"
python "$BOULEVARD_HOME/main.py" "\$@"
EOL
chmod +x "$BOULEVARD_CMD"

# Create convenient aliases
echo -e "${BLUE}Setting up Boulevard aliases...${NC}"
SHELL_RC="$HOME/.bashrc"
if [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
fi

# Add Boulevard to PATH and create aliases
echo "" >> "$SHELL_RC"
echo "# Boulevard Configuration" >> "$SHELL_RC"
echo "export PATH=\"\$PATH:$BOULEVARD_HOME\"" >> "$SHELL_RC"
echo "alias boulevard='$BOULEVARD_HOME/boulevard'" >> "$SHELL_RC"
echo "alias blvd='$BOULEVARD_HOME/boulevard'" >> "$SHELL_RC"

# Run the installer
echo -e "${BLUE}Running Boulevard installer...${NC}"
"$BOULEVARD_HOME/venv/bin/python" "$BOULEVARD_HOME/install.py"

# Final setup steps
echo -e "${GREEN}Boulevard has been successfully deployed!${NC}"
echo -e "${GREEN}Installation complete! To get started:${NC}"
echo -e "${BLUE}1. Edit your configuration:${NC}"
echo "   nano ~/.boulevard/config/config.json"
echo -e "${BLUE}2. Start Boulevard:${NC}"
echo "   boulevard"
echo ""
echo -e "${BLUE}You can also use these commands:${NC}"
echo "   boulevard --status    # Check system status"
echo "   boulevard --activity  # View recent activity"
echo "   boulevard --stats     # View performance statistics"
echo ""
echo -e "${RED}Important:${NC} Please restart your terminal or run 'source $SHELL_RC'"
echo "to use the 'boulevard' command directly."

# Cleanup
cleanup

echo -e "${GREEN}🌅 Boulevard deployment complete!${NC}"
