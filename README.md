# Termux AI Agent (Web-Centric Edition)

This project is a full-stack, AI-powered autonomous agent designed to run entirely within a Termux environment on Android. It features a web-based UI, a sandboxed browser for tool use, and a powerful FastAPI backend, all orchestrated to provide a rich, interactive agent experience on a mobile device.

## Architecture Overview

The agent is composed of several key components that work together:

-   **Web Frontend (Vue/Vite):** A modern, reactive user interface running on port `5173`. This is the primary way to interact with the agent. It includes a chat interface and an embedded noVNC viewer for the sandboxed browser.
-   **Main Backend (FastAPI):** The primary server running on port `8000`. It manages agent sessions, communicates with the AI model (Gemini), and streams events to the frontend via Server-Sent Events (SSE).
-   **Sandbox API (FastAPI):** A secondary server running on port `8080`. This server runs *inside* the sandbox and exposes an API for the main backend to control tools within the isolated environment.
-   **Sandbox Environment (proot-distro):** An Ubuntu environment running under `proot-distro`. This is where all potentially unsafe operations, like running a web browser or executing code, take place.
-   **Browser Tools (XVFB + Chromium + VNC):** A full-featured Chromium browser runs headlessly inside the sandbox using a virtual display (XVFB). Its interface is served via a VNC server on port `5900` and proxied by `websockify` on port `6080` to be compatible with the noVNC web client.

## Setup Instructions

This guide will walk you through setting up the entire environment from a fresh Termux installation.

### Step 1: Install Termux Base Dependencies

First, run the script to install the necessary packages in your main Termux environment.

```bash
bash scripts/install_termux_deps.sh
```

### Step 2: Install and Set Up the Ubuntu Sandbox

Next, install the Ubuntu distribution using `proot-distro` and then run the setup script *inside* it.

1.  **Install the distro:**
    ```bash
    proot-distro install ubuntu
    ```
2.  **Log in to the distro:**
    ```bash
    proot-distro login ubuntu
    ```
3.  **Inside Ubuntu, run the setup script:**
    You will need to navigate to the project directory. The Termux home directory is typically mounted at `/data/data/com.termux/files/home`.
    ```bash
    # Inside the Ubuntu session
    cd /data/data/com.termux/files/home/TermuxAgent # Adjust path if needed
    bash scripts/setup_ubuntu.sh
    exit # Exit the Ubuntu session when done
    ```

### Step 3: Configure the Agent

Copy the example configuration file and add your Gemini API key.

```bash
cp backend/config.json.example backend/config.json
nano backend/config.json
```

## Running the Agent

To run the agent, you need to start all of its services. The provided `run_agent.sh` script automates most of this.

1.  **Start the services:**
    From the project root directory, run the master script:
    ```bash
    bash scripts/run_agent.sh
    ```
2.  **Follow the On-Screen Instructions:**
    The script will start the backend servers and the frontend dev server. It will then prompt you to open a **new Termux session** to start the browser tools inside the Ubuntu sandbox. Follow the instructions printed in the terminal carefully.

## Verification

Once all services are running, you can verify that everything is working correctly:

1.  **Web Frontend:** Open a browser on your Android device (or another device on the same network) and navigate to `http://<your-termux-ip>:5173`. You should see the Vue frontend load.
2.  **Backend Connection:** The chat UI should connect to the backend, and you should see system events streamed from the server.
3.  **Browser Tool:** The `ToolPanel.vue` component should display the noVNC interface, showing the desktop of the sandboxed Chromium browser.
4.  **Chrome DevTools:** You can access the Chrome DevTools Protocol for the sandboxed browser at `http://<your-termux-ip>:9222`.
