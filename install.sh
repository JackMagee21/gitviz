#!/usr/bin/env bash
# gitviz installer for Mac and Linux
# Run from the root of the cloned repository:
#   bash scripts/install.sh

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # no colour

echo ""
echo -e "${CYAN}gitviz installer${NC}"
echo -e "${CYAN}----------------${NC}"

# 1. Check Python
echo ""
echo -e "${YELLOW}Checking Python...${NC}"
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}ERROR: python3 not found.${NC}"
    echo "Install it from https://python.org or via your package manager:"
    echo "  Mac:    brew install python"
    echo "  Ubuntu: sudo apt install python3 python3-pip"
    exit 1
fi
echo -e "${GREEN}Found $(python3 --version)${NC}"

# 2. Install the package
echo ""
echo -e "${YELLOW}Installing gitviz...${NC}"
python3 -m pip install . --quiet
echo -e "${GREEN}Package installed.${NC}"

# 3. Find the scripts/bin folder
echo ""
echo -e "${YELLOW}Locating install directory...${NC}"
SCRIPTS_DIR=$(python3 -m pip show gitviz | grep "^Location:" | sed 's/Location: //')

# On Mac/Linux pip installs scripts to a bin directory relative to the Python prefix
BIN_DIR=$(python3 -c "import sysconfig; print(sysconfig.get_path('scripts'))")
echo -e "${GREEN}Found: $BIN_DIR${NC}"

# 4. Check if already on PATH
if echo "$PATH" | tr ':' '\n' | grep -qx "$BIN_DIR"; then
    echo -e "${GREEN}Install directory is already on PATH.${NC}"
else
    echo ""
    echo -e "${YELLOW}Adding $BIN_DIR to PATH...${NC}"

    # Detect shell config file
    if [ -f "$HOME/.zshrc" ]; then
        SHELL_RC="$HOME/.zshrc"
    elif [ -f "$HOME/.bashrc" ]; then
        SHELL_RC="$HOME/.bashrc"
    elif [ -f "$HOME/.bash_profile" ]; then
        SHELL_RC="$HOME/.bash_profile"
    else
        SHELL_RC="$HOME/.profile"
    fi

    echo "" >> "$SHELL_RC"
    echo "# Added by gitviz installer" >> "$SHELL_RC"
    echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$SHELL_RC"

    echo -e "${GREEN}Added to $SHELL_RC${NC}"
fi

# 5. Done
echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo -e "${CYAN}IMPORTANT: Open a new terminal window, then run:${NC}"
echo "  gitviz --help"
echo ""
echo "Or reload your shell config now with:"
echo "  source $SHELL_RC"
echo ""