# CRM Meeting App

A desktop CRM application for recording, transcribing, and summarizing meetings with LP/GP partners.

## Features

- **Meeting Recording**: Record audio from both system audio and microphone
- **AI Transcription**: Automatic transcription using Whisper (via local AI server)
- **AI Summarization**: Generate meeting summaries using local LLM
- **Contact Management**: Track LPs, GPs, and individual contacts
- **Sales Funnel**: Track fundraising stages and interest levels
- **Action Items**: Automatic extraction and tracking of todos
- **Local-First**: All data stored locally in SQLite database

## Tech Stack

### Frontend
- **Svelte** - Reactive UI framework
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool

### Backend
- **Tauri** - Rust-based desktop framework
- **Python + FastAPI** - REST API backend
- **SQLModel** - Type-safe ORM (SQLAlchemy + Pydantic)
- **SQLite** - Local database

### AI Integration
- **Whisper** - Speech-to-text (via office server)
- **Ollama** - Local LLM inference (via office server)

## Project Structure

```
meeting_app/
├── src/                          # Svelte frontend
│   ├── App.svelte
│   ├── main.ts
│   ├── components/
│   │   ├── LPSection.svelte
│   │   ├── GPSection.svelte
│   │   ├── MeetingMeta.svelte
│   │   ├── NotesEditor.svelte
│   │   └── TodoList.svelte
│   └── lib/
│       ├── api.ts                # API client
│       └── stores.ts             # State management
│
├── src-tauri/                    # Tauri backend
│   ├── src/main.rs               # Rust entrypoint
│   ├── Cargo.toml
│   ├── tauri.conf.json
│   └── python/
│       ├── backend.py            # FastAPI router
│       ├── database.py           # SQLModel models
│       ├── audio_service.py      # Audio recording
│       ├── transcription_service.py   # Whisper integration
│       └── summarization_agent.py     # LLM summarization
│
├── db/                           # Local data
│   ├── crm.db                    # SQLite database
│   └── recordings/               # Audio files
│
├── package.json
├── requirements.txt
└── README.md
```

## Prerequisites

- **Python 3.13+** ✓ (installed)
- **Node.js 18+** ✓ (v24.3.0 installed)
- **Rust & Cargo** ✓ (v1.90.0 installed)
- **Tauri CLI** ✓ (v2.9.1 installed)

## Setup Instructions

### 1. Clone and Navigate to Project

```bash
cd "/Users/lvc/AI Scripts/2025_10 CRM App"
```

### 2. Install Python Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Note**: PyAudio may require PortAudio. Install with:
```bash
brew install portaudio
```

### 3. Initialize Database

```bash
python3 src-tauri/python/database.py
```

This creates the SQLite database at `db/crm.db`.

### 4. Install Node Dependencies

```bash
npm install
```

### 5. Run Development Server

In one terminal, start the Python backend:
```bash
source venv/bin/activate
python3 src-tauri/python/backend.py
```

In another terminal, start the Tauri app:
```bash
npm run tauri:dev
```

## AI Server Configuration

The app is designed to connect to your office AI server for:
- **Transcription**: Whisper API endpoint
- **Summarization**: Ollama API endpoint

### Configure Server URL

Update the server URLs in:
- `src-tauri/python/transcription_service.py` (line 13)
- `src-tauri/python/summarization_agent.py` (line 13)

Default: `http://localhost:11434` (Ollama default)

Example for custom server:
```python
# In transcription_service.py
self.server_url = "http://your-office-server:8000"

# In summarization_agent.py
self.server_url = "http://your-office-server:11434"
```

### Test Server Connection

```bash
python3 src-tauri/python/transcription_service.py
python3 src-tauri/python/summarization_agent.py
```

## Database Schema

### Tables

**LP** - Limited Partners
- id (PK)
- name

**GP** - General Partners
- id (PK)
- name

**Person** - Individual Contacts
- id (PK)
- name, role, org_type, org_id
- email, phone

**Note** - Meeting Notes
- id (PK)
- date, lp_id (FK), gp_id (FK)
- raw_notes, summary
- fundraise, interest
- audio_path, transcription_path

**Todo** - Action Items
- id (PK)
- note_id (FK)
- description, status, due_date

## API Endpoints

Backend runs on `http://localhost:8000`

### Health Check
- `GET /health` - Check backend status

### LPs
- `GET /lps` - List all LPs
- `POST /lps` - Create LP
- `DELETE /lps/{id}` - Delete LP

### GPs
- `GET /gps` - List all GPs
- `POST /gps` - Create GP
- `DELETE /gps/{id}` - Delete GP

### People
- `GET /people` - List all people
- `POST /people` - Create person

### Notes
- `GET /notes` - List all notes
- `GET /notes/{id}` - Get specific note
- `POST /notes` - Create note
- `PUT /notes/{id}` - Update note

### Todos
- `GET /todos` - List all todos
- `POST /todos` - Create todo
- `PUT /todos/{id}` - Update todo

## Building for Production

```bash
npm run tauri:build
```

The built app will be in `src-tauri/target/release/`.

## Migration Path (Future)

| Current | Future | Effort |
|---------|--------|--------|
| SQLite (local) | PostgreSQL (shared) | Update connection string |
| Svelte | React/Next.js | Replace UI, reuse API |
| Tauri desktop | Web dashboard | Expose FastAPI over HTTPS |
| Ollama local | Remote/hybrid inference | Drop-in replacement |

## Development Notes

### Auto-save
Notes auto-save every 10 seconds while typing.

### Audio Devices
List available input devices:
```bash
python3 src-tauri/python/audio_service.py
```

### Database Migrations
SQLModel will auto-create tables on first run. For schema changes, consider:
- Alembic for migrations
- Or manually update via SQL scripts

## Troubleshooting

### PyAudio won't install
```bash
brew install portaudio
pip install --global-option='build_ext' --global-option='-I/opt/homebrew/include' --global-option='-L/opt/homebrew/lib' pyaudio
```

### Tauri build fails
Ensure Rust is in PATH:
```bash
source "$HOME/.cargo/env"
```

### Backend not connecting
Check FastAPI is running on port 8000:
```bash
lsof -i :8000
```

### AI server not reachable
Verify server URL and test connection:
```bash
curl http://your-server:11434/api/tags
```

## Next Steps

1. **Test the skeleton**: Run `npm run tauri:dev`
2. **Configure AI server**: Update URLs when office server is ready
3. **Add icons**: Place app icons in `src-tauri/icons/`
4. **Customize**: Extend features as needed

## GitHub Repository

```bash
git remote add origin https://github.com/louisv1148/2025_10-CRM-App.git
```

## License

Private project - All rights reserved

---

**Generated**: 2025-10-24
**Author**: Louis V
**Stack**: Tauri + Svelte + Python + FastAPI + SQLModel
