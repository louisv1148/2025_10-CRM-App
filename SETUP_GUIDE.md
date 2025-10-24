# Complete Setup Guide

## Quick Setup (Recommended)

Run the automated installer:

```bash
cd "/Users/lvc/AI Scripts/2025_10 CRM App"
./setup/install.sh
```

This will:
- ✅ Check all prerequisites (Python, Node, Rust)
- ✅ Create all required directories
- ✅ Install Python dependencies in virtual environment
- ✅ Install Node dependencies
- ✅ Initialize SQLite database with schema
- ✅ Seed example data (LPs, GPs, notes, todos)

## Manual Setup (Alternative)

If you prefer step-by-step control:

### 1. Prerequisites Check

```bash
python3 --version  # Should be 3.13+
node --version     # Should be 18+
cargo --version    # Should be installed
```

### 2. Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv src-tauri/python/lib
source src-tauri/python/lib/bin/activate

# Install packages
pip install --upgrade pip
pip install -r requirements.txt
```

**macOS PyAudio Fix** (if needed):
```bash
brew install portaudio
pip install pyaudio
```

### 3. Install Node Dependencies

```bash
npm install
```

### 4. Initialize Database

```bash
python3 setup/setup.py
```

This creates:
- `db/crm.db` - SQLite database
- `data/recordings/` - Audio files
- `data/transcripts/` - Transcription text
- `data/summaries/` - AI summaries

## Running the App

### Development Mode

**Terminal 1** - Backend API:
```bash
cd "/Users/lvc/AI Scripts/2025_10 CRM App"
source src-tauri/python/lib/bin/activate
python3 src-tauri/python/backend.py
```

Or using npm script:
```bash
npm run backend
```

**Terminal 2** - Tauri Desktop App:
```bash
npm run tauri:dev
```

### First Time Launch

The app will:
1. Compile Rust code (takes 2-3 minutes first time)
2. Start Vite dev server (http://localhost:1420)
3. Open desktop window with the app

Subsequent launches are much faster (~10 seconds).

## Verify Installation

### 1. Check Backend

```bash
# In activated venv
curl http://localhost:8000/health
```

Expected: `{"status":"ok","timestamp":"2025-10-24T..."}`

### 2. Check Database

```bash
sqlite3 db/crm.db "SELECT * FROM lp;"
```

Expected:
```
1|Example LP Fund
2|Demo Capital Partners
```

### 3. List All Tables

```bash
npm run db:view
```

Then run:
```sql
.tables
.schema note
SELECT * FROM note;
.quit
```

## NPM Scripts Reference

```bash
# Setup
npm run setup          # Run full installation

# Development
npm run dev            # Vite only (frontend)
npm run backend        # Python backend only
npm run tauri:dev      # Full app (Tauri + Vite)

# Database
npm run db:init        # Initialize database
npm run db:view        # Open SQLite CLI

# Production
npm run build          # Build frontend
npm run tauri:build    # Build desktop app
```

## Project Structure After Setup

```
2025_10 CRM App/
├── setup/
│   ├── install.sh ✓          # Installer script
│   └── setup.py ✓            # Database initializer
│
├── src-tauri/python/lib/     # Python venv (created by installer)
│   ├── bin/activate
│   └── lib/python3.13/...
│
├── db/
│   └── crm.db ✓              # SQLite database (created by setup.py)
│
├── data/
│   ├── recordings/ ✓
│   ├── transcripts/ ✓
│   └── summaries/ ✓
│
└── node_modules/ ✓           # Node packages (created by npm install)
```

## Developer Workflow

### Standard Development Cycle

1. **Make code changes** in `src/` (Svelte) or `src-tauri/python/` (Python)
2. **Hot reload** happens automatically for frontend
3. **Restart backend** manually for Python changes:
   ```bash
   # Ctrl+C in backend terminal, then:
   python3 src-tauri/python/backend.py
   ```
4. **Reload Tauri** for Rust changes:
   ```bash
   # Ctrl+C in tauri terminal, then:
   npm run tauri:dev
   ```

### Testing Backend API

Start backend and use curl or browser:

```bash
# List all LPs
curl http://localhost:8000/lps

# Create new LP
curl -X POST http://localhost:8000/lps \
  -H "Content-Type: application/json" \
  -d '{"name":"New Fund LP"}'

# Get all notes
curl http://localhost:8000/notes

# API docs (Swagger)
open http://localhost:8000/docs
```

### Database Operations

```bash
# View tables
sqlite3 db/crm.db ".tables"

# Check LP records
sqlite3 db/crm.db "SELECT * FROM lp;"

# Check recent notes
sqlite3 db/crm.db "SELECT id, date, summary FROM note ORDER BY date DESC LIMIT 5;"

# Delete all data (reset)
rm db/crm.db
python3 setup/setup.py
```

## Troubleshooting

### "Python not found"
```bash
# macOS
brew install python@3.13

# Or use system Python
which python3
```

### "Cargo not found"
```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
```

### "Port 8000 already in use"
```bash
# Find and kill process
lsof -i :8000
kill -9 <PID>
```

### "PyAudio failed to install"
```bash
# Install PortAudio first
brew install portaudio

# Then reinstall PyAudio
pip install --force-reinstall pyaudio
```

### "Tauri build fails"
```bash
# Ensure Rust is in PATH
source "$HOME/.cargo/env"

# Update Rust
rustup update

# Clean build
cd src-tauri
cargo clean
cd ..
npm run tauri:dev
```

### "Database locked"
```bash
# Close all connections
pkill -f backend.py

# Check for lock
ls -la db/

# Remove lock file if exists
rm db/crm.db-journal
```

### "Frontend won't connect to backend"
Check that:
1. Backend is running on port 8000
2. CORS is enabled (already configured in backend.py)
3. API_BASE_URL in `src/lib/api.ts` is correct

## Next Steps

After successful setup:

1. **Explore the UI**: Run `npm run tauri:dev` and test all tabs
2. **Add real data**: Create your LPs/GPs through the interface
3. **Test recording**: Click "Start Recording" (requires PyAudio)
4. **Configure AI server**: Update URLs when office server is ready
5. **Customize**: Modify components in `src/components/`

## Production Build

To create distributable app:

```bash
npm run tauri:build
```

Output: `src-tauri/target/release/bundle/`

macOS: `.dmg` and `.app` files
Windows: `.exe` installer
Linux: `.deb`, `.AppImage`

---

**Questions?** Check [README.md](README.md) or [QUICKSTART.md](QUICKSTART.md)
