#!/bin/bash
#
# This script installs dependencies within the proot-distro Ubuntu environment.
# It should be executed after logging into the distro.
#

echo "--- Installing Dependencies inside Ubuntu Sandbox ---"

# Update package lists
apt-get update -y && apt-get upgrade -y

# Install dependencies for running a headless browser with VNC
# python3-pip - To install Python packages
# nodejs, npm - In case they are needed for any tools inside the sandbox
# xvfb - The virtual framebuffer for running GUI apps without a display
# x11vnc - A VNC server
# chromium-browser - The browser to be controlled by the agent
apt-get install -y python3-pip nodejs npm xvfb x11vnc chromium-browser

# Install websockify, which is needed to proxy the VNC connection for noVNC
pip3 install websockify

echo "--- Ubuntu sandbox setup complete. ---"
echo "You can now run the browser tools from this environment."
