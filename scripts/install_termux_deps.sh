#!/bin/bash
#
# This script installs the base dependencies required on the main Termux environment.
#

echo "--- Installing Termux Base Dependencies ---"

# Update package lists and upgrade existing packages
pkg update -y && pkg upgrade -y

# Install essential packages
# nodejs - For the Vite frontend
# python - For the FastAPI backend
# rust, clang, cmake - Often required for building Python package dependencies
# proot-distro - For sandboxing
# wget, curl, unzip - General utilities
pkg install -y git nodejs python rust clang cmake proot-distro wget curl unzip

echo "--- Base dependencies installed successfully. ---"
echo "Next, run 'proot-distro install ubuntu' to set up the sandbox."
echo "Then, use 'proot-distro login ubuntu' and run 'scripts/setup_ubuntu.sh' inside the sandbox."
