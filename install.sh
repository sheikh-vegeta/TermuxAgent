#!/bin/bash

# This script automates the setup of the Termux AI Agent.

echo "--- Starting Termux AI Agent Setup ---"

# --- Step 1: Update packages and install dependencies ---
echo ">>> Updating Termux packages and installing core dependencies..."
pkg update -y && pkg upgrade -y
pkg install -y python git proot-distro

# Check if installation was successful
if ! command -v python &> /dev/null || ! command -v git &> /dev/null; then
    echo "Error: Failed to install core dependencies (Python, Git). Please run 'pkg install python git' manually."
    exit 1
fi

# --- Step 2: Set up Python dependencies ---
echo ">>> Installing Python packages from requirements.txt..."
if [ -f "backend/requirements.txt" ]; then
    pip install -r backend/requirements.txt
else
    echo "Error: backend/requirements.txt not found. Please ensure you are in the project root directory."
    exit 1
fi

# --- Step 3: Set up sandbox environment ---
echo ">>> Setting up sandbox environment (proot-distro alpine)..."
proot-distro install alpine

echo "--- Setup Complete! ---"
echo "Next steps:"
echo "1. Create a config file: 'cp backend/config.json.example backend/config.json'"
echo "2. Edit 'backend/config.json' to add your Gemini API key."
echo "3. Start the agent's backend server: 'cd backend && uvicorn main:app --host 0.0.0.0 --port 8000'"
echo "4. In another Termux session, use the CLI: 'python backend/cli.py --help'"
