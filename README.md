# Termux AI Agent

An AI-powered autonomous coding agent designed to run directly within the Termux environment on Android. This agent can help with code generation, refactoring, debugging, and more, using Google's Gemini API and a command-line interface.

## Features

- **Termux-Native:** Runs entirely within the Termux terminal, with no external dependencies on desktop IDEs.
- **AI-Powered Coding:** Uses the Gemini API for intelligent code analysis, generation, and refactoring.
- **Command-Line Interface:** Interact with the agent through a simple and powerful CLI built with Click.
- **Safe Execution:** Utilizes `proot-distro` to execute code in a sandboxed Alpine Linux environment, preventing accidental damage to your system.
- **Automated Setup:** A simple `install.sh` script to set up all dependencies in Termux.
- **Configurable:** Uses a `config.json` file to manage API keys and user preferences.
- **Extensible:** Built with a modular structure (`main.py`, `mcp.py`, `safety.py`) that is easy to extend.

## Setup Instructions

These instructions will guide you through setting up the Termux AI Agent on your Android device.

### 1. Install Termux
First, install the Termux application from F-Droid. It is the recommended source for the latest, most stable version.

### 2. Clone the Repository
Open Termux and install `git`, then clone this repository:
```bash
pkg update -y && pkg install -y git
git clone https://github.com/sheikh-vegeta/TermuxAgent.git
cd TermuxAgent
```

### 3. Run the Installer
Execute the installation script. This will install all necessary packages, Python dependencies, and set up the sandbox environment.
```bash
bash install.sh
```

### 4. Configure the Agent
Create your configuration file from the example template and add your Gemini API key.

1.  **Copy the config file:**
    ```bash
    cp backend/config.json.example backend/config.json
    ```
2.  **Edit the config file:**
    Use a terminal editor like `nano` or `vim` to edit `backend/config.json` and insert your API key.
    ```bash
    nano backend/config.json
    ```

## Usage

The agent consists of a backend server and a CLI client. You will need to run them in separate Termux sessions.

### Session 1: Start the Backend Server
In your first Termux session, navigate to the `backend` directory and start the FastAPI server with `uvicorn`.
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```
The server will now be running and listening for requests.

### Session 2: Use the CLI Client
Open a new Termux session (swipe from the left edge and tap "New Session"). In this new session, you can use the `cli.py` script to interact with the agent.

**Get help:**
```bash
python backend/cli.py --help
```

**Example: Refactor a file**
To ask the AI to refactor a function in a file named `my_script.py`:
```bash
python backend/cli.py refactor "Make this function more efficient and add comments" --file my_script.py
```

**Example: Refactor a specific selection**
To refactor lines 10 through 25 of `my_script.py`:
```bash
python backend/cli.py refactor "Rename the variables to be more descriptive" --file my_script.py --line-start 10 --line-end 25
```

**Example: Use dry-run**
To see the suggested changes without applying them, use the `--dry-run` flag:
```bash
python backend/cli.py refactor "Convert this to a list comprehension" --file my_script.py --dry-run
```

**Example: Update the agent**
To pull the latest changes from the GitHub repository:
```bash
python backend/cli.py self-update
```
---
*This project is under active development.*
