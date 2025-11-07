#!/bin/bash

# CRM App Launcher Script
# Double-click this file to start the CRM application

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Function to cleanup on exit
cleanup() {
    echo "Shutting down CRM application..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    exit 0
}

trap cleanup EXIT INT TERM

# Open a new terminal window for the backend
echo "Starting CRM Backend Server..."
osascript -e 'tell application "Terminal"
    do script "cd \"'"$SCRIPT_DIR"'\" && source src-tauri/python/lib/bin/activate && python3 src-tauri/python/backend.py"
end tell'

# Wait a moment for backend to start
echo "Waiting for backend to initialize..."
sleep 3

# Start the frontend in the current terminal
echo "Starting CRM Frontend..."
echo "The application window will open shortly..."
npm run tauri dev

# When frontend closes, cleanup
cleanup
