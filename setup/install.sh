#!/bin/bash
echo "🔧 Setting up MeetingApp..."

# Ensure python is installed
if ! command -v python3 &> /dev/null
then
    echo "❌ Python3 not found. Please install Python 3.13 before continuing."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2 | cut -d '.' -f 1,2)
echo "✓ Found Python $PYTHON_VERSION"

# Ensure Node is installed
if ! command -v node &> /dev/null
then
    echo "❌ Node.js not found. Please install Node.js 18+ before continuing."
    exit 1
fi

NODE_VERSION=$(node --version)
echo "✓ Found Node $NODE_VERSION"

# Ensure Rust/Cargo is installed
# Try to source cargo env first
if [ -f "$HOME/.cargo/env" ]; then
    source "$HOME/.cargo/env"
fi

if ! command -v cargo &> /dev/null
then
    echo "❌ Cargo not found. Please install Rust before continuing."
    echo "Run: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    echo "Then run this script again."
    exit 1
fi

CARGO_VERSION=$(cargo --version)
echo "✓ Found $CARGO_VERSION"

# Create directories
echo "📁 Creating directories..."
mkdir -p db data/recordings data/transcripts data/summaries src-tauri/python/lib

# Install Python dependencies locally
echo "📦 Installing Python dependencies..."
python3 -m venv src-tauri/python/lib
source src-tauri/python/lib/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Check if PyAudio failed (common issue on macOS)
if ! python3 -c "import pyaudio" 2>/dev/null; then
    echo "⚠️  PyAudio installation may have failed."
    echo "If you need audio recording, install PortAudio first:"
    echo "  brew install portaudio"
    echo "  pip install pyaudio"
fi

# Initialize database
echo "🗄️  Initializing database..."
python3 setup/setup.py

# Install Node dependencies
echo "📦 Installing Node dependencies..."
npm install

echo ""
echo "✅ MeetingApp setup complete!"
echo ""
echo "Next steps:"
echo "  1. Start the backend:  source src-tauri/python/lib/bin/activate && python3 src-tauri/python/backend.py"
echo "  2. Start the app:      npm run tauri:dev"
echo ""
