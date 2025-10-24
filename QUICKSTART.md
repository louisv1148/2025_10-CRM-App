# Quick Start Guide

Get the CRM Meeting App running in 5 minutes!

## Prerequisites Check

All prerequisites are already installed on your system:
- ✅ Python 3.13.0
- ✅ Node.js v24.3.0
- ✅ Rust 1.90.0
- ✅ Tauri CLI 2.9.1

## Installation Steps

### 1. Install Python Dependencies

```bash
cd "/Users/lvc/AI Scripts/2025_10 CRM App"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Note**: If PyAudio fails to install:
```bash
brew install portaudio
pip install pyaudio
```

### 2. Install Node Dependencies

```bash
npm install
```

### 3. Initialize Database

```bash
source venv/bin/activate
python3 src-tauri/python/database.py
```

## Running the App

### Option 1: Development Mode (Recommended)

**Terminal 1** - Start Python backend:
```bash
cd "/Users/lvc/AI Scripts/2025_10 CRM App"
source venv/bin/activate
python3 src-tauri/python/backend.py
```

**Terminal 2** - Start Tauri app:
```bash
cd "/Users/lvc/AI Scripts/2025_10 CRM App"
npm run tauri:dev
```

### Option 2: Frontend Only (Testing UI)

```bash
npm run dev
```
Then open http://localhost:1420 in your browser.

## Verify Installation

1. **Backend Health Check**:
```bash
curl http://localhost:8000/health
```
Should return: `{"status":"ok","timestamp":"..."}`

2. **Test Database**:
```bash
source venv/bin/activate
python3 -c "from src_tauri.python.database import create_db_and_tables; create_db_and_tables(); print('✓ Database OK')"
```

3. **Check Audio Devices**:
```bash
source venv/bin/activate
python3 src-tauri/python/audio_service.py
```

## Project Structure (Quick Reference)

```
2025_10 CRM App/
├── src/                    # Svelte frontend
│   ├── App.svelte         # Main app component
│   ├── components/        # UI components
│   ├── lib/api.ts        # Backend API client
│   └── lib/stores.ts     # State management
│
├── src-tauri/python/      # Python backend
│   ├── backend.py        # FastAPI server
│   ├── database.py       # SQLModel ORM
│   ├── audio_service.py  # Audio recording
│   ├── transcription_service.py
│   └── summarization_agent.py
│
├── db/crm.db             # SQLite database
└── data/                 # Recordings & transcripts
```

## Common Commands

```bash
# Start development
npm run tauri:dev

# Run tests
pytest src-tauri/python/

# Build for production
npm run tauri:build

# Push to GitHub
git push -u origin master
```

## Next Steps

1. **Configure AI Server**: Update URLs in transcription/summarization services
2. **Test Recording**: Click "Start Recording" button in the app
3. **Add Sample Data**: Create test LPs/GPs through the UI
4. **Customize**: Modify components in `src/components/`

## Troubleshooting

### "Port 8000 already in use"
```bash
lsof -i :8000
kill -9 <PID>
```

### "Tauri command not found"
```bash
source "$HOME/.cargo/env"
```

### "Database locked"
Close any SQLite browsers and restart the backend.

## Resources

- Full docs: See [README.md](README.md)
- API endpoints: http://localhost:8000/docs (when backend is running)
- GitHub: https://github.com/louisv1148/2025_10-CRM-App

---

**Ready to start?** Run the commands above and you'll be recording meetings in minutes!
