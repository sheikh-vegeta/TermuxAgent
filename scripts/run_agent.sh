#!/bin/bash
#
# This script starts all the services for the Termux AI Agent.
# It should be run from the project's root directory.
#

echo "--- Starting Termux AI Agent Services ---"

# --- Start Backend Servers ---
echo ">>> Starting FastAPI main server on port 8000..."
cd backend
uvicorn main_server:app --host 0.0.0.0 --port 8000 &
MAIN_PID=$!
cd ..

echo ">>> Starting FastAPI sandbox API on port 8080..."
# This would typically be started from within the proot-distro environment
# For now, we'll launch it from the host as a placeholder.
cd backend
uvicorn sandbox_api:app --host 0.0.0.0 --port 8080 &
SANDBOX_API_PID=$!
cd ..

# --- Start Frontend Dev Server ---
echo ">>> Starting Vite frontend dev server on port 5173..."
cd frontend
npm install
npm run dev &
FRONTEND_PID=$!
cd ..

# --- Start Sandbox Browser Tools (inside proot-distro) ---
# These commands need to be run inside the Ubuntu sandbox.
# This script can't log in automatically, so these are instructions for the user.
echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
echo "!!! ACTION REQUIRED: Start Browser Tools in another session! !!!"
echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
echo "In a new Termux session, run the following commands:"
echo "1. proot-distro login ubuntu"
echo "2. xvfb-run -s '-screen 0 1024x768x24' chromium-browser --remote-debugging-port=9222 --no-sandbox &"
echo "3. x11vnc -display :99 -forever -nopw -listen 0.0.0.0 -rfbport 5900 &"
echo "4. websockify 6080 localhost:5900 &"
echo "--------------------------------------------------------------"


echo "--- All services started. ---"
echo "Main Server PID: $MAIN_PID"
echo "Sandbox API PID: $SANDBOX_API_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "Press Ctrl+C to stop all services."

# Trap Ctrl+C and kill all background processes
trap "echo '--- Shutting down services ---'; kill $MAIN_PID $SANDBOX_API_PID $FRONTEND_PID; exit" INT

# Wait indefinitely
wait
