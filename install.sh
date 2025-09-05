#!/bin/bash
set -e

# Helper functions for colored output
info() {
    echo -e "\033[1;34m[INFO]\033[0m $1"
}

success() {
    echo -e "\033[1;32m[SUCCESS]\033[0m $1"
}

error() {
    echo -e "\033[1;31m[ERROR]\033[0m $1" >&2
    exit 1
}

# --- Main Installation Logic ---

info "Starting the Termux AI Agent installation..."

# Step 1: Install Termux base dependencies
info "Step 1/4: Installing Termux base dependencies..."
if bash scripts/install_termux_deps.sh; then
    success "Termux dependencies installed successfully."
else
    error "Failed to install Termux dependencies."
fi

# Step 2: Install the Ubuntu proot-distro sandbox
info "Step 2/4: Setting up the Ubuntu sandbox..."
if proot-distro list | grep -q "ubuntu"; then
    info "Ubuntu distro already installed. Skipping."
else
    info "Installing Ubuntu distro via proot-distro..."
    if proot-distro install ubuntu; then
        success "Ubuntu distro installed successfully."
    else
        error "Failed to install Ubuntu distro."
    fi
fi

# Step 3: Run the setup script inside the Ubuntu sandbox
info "Step 3/4: Running setup script inside Ubuntu..."
# Get the absolute path to the project directory to make it accessible inside the sandbox
PROJECT_DIR=$(pwd)
SETUP_SCRIPT_PATH="$PROJECT_DIR/scripts/setup_ubuntu.sh"

info "Executing setup script at $SETUP_SCRIPT_PATH..."
if proot-distro login ubuntu -- bash "$SETUP_SCRIPT_PATH"; then
    success "Ubuntu setup script executed successfully."
else
    error "Failed to execute Ubuntu setup script."
fi

# Step 4: Create the initial configuration file
info "Step 4/4: Creating initial configuration file..."
CONFIG_FILE="backend/config.json"
CONFIG_EXAMPLE_FILE="backend/config.json.example"

if [ -f "$CONFIG_FILE" ]; then
    info "Configuration file '$CONFIG_FILE' already exists. Skipping."
else
    if [ -f "$CONFIG_EXAMPLE_FILE" ]; then
        cp "$CONFIG_EXAMPLE_FILE" "$CONFIG_FILE"
        success "Created configuration file '$CONFIG_FILE'."
        info "IMPORTANT: You must now edit '$CONFIG_FILE' and add your API keys."
    else
        error "Configuration example file '$CONFIG_EXAMPLE_FILE' not found!"
    fi
fi

echo
success "Installation complete!"
info "To run the agent, you can now use the 'bash scripts/run_agent.sh' script."
info "Remember to fill in your API keys in 'backend/config.json' before running the agent."
