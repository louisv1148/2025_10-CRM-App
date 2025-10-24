# 🧠 Developer Notes — MeetingApp

**Version**: 0.1
**Author**: Louis Viramontes
**Purpose**: Local-first meeting recording and CRM data capture app
**Stack**: Svelte + Tauri + Python (FastAPI) + SQLite
**AI Integrations**: Whisper CPP (transcription) + Ollama (summarization)

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         TAURI DESKTOP APP                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    SVELTE FRONTEND                         │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │  │
│  │  │ LP/GP    │  │ Meeting  │  │  Notes   │  │  ToDo    │  │  │
│  │  │ Section  │  │   Meta   │  │  Editor  │  │  List    │  │  │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │  │
│  │       │             │              │             │         │  │
│  │       └─────────────┴──────────────┴─────────────┘         │  │
│  │                          │                                  │  │
│  │                    ┌─────▼─────┐                           │  │
│  │                    │  api.ts   │  (Tauri invoke bridge)    │  │
│  │                    └─────┬─────┘                           │  │
│  └──────────────────────────┼─────────────────────────────────┘  │
│                             │                                     │
│  ┌──────────────────────────▼─────────────────────────────────┐  │
│  │                   RUST MAIN.RS                             │  │
│  │  (Command handlers: start_recording, transcribe, etc.)     │  │
│  └──────────────────────────┬─────────────────────────────────┘  │
└─────────────────────────────┼───────────────────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │   PYTHON BACKEND   │
                    │   (FastAPI)        │
                    └─────────┬──────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐         ┌──────▼──────┐      ┌──────▼──────┐
   │  SQLite │         │   Whisper   │      │   Ollama    │
   │ Database│         │  CPP (local)│      │  (local AI) │
   │ crm.db  │         │             │      │             │
   └─────────┘         └─────────────┘      └─────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
   [LP/GP/Note]       [Transcripts]          [Summaries]
   [Person/Todo]      data/transcripts/      data/summaries/
```

**Data Flow**:
1. User interacts with **Svelte UI**
2. UI calls backend via **Tauri invoke** (Rust bridge)
3. **FastAPI** handles business logic
4. **SQLite** stores structured data
5. **Whisper** transcribes audio recordings
6. **Ollama** generates summaries from transcripts

---

## 🗂️ Project Overview

```
MeetingApp/
├── src/                     # Frontend (Svelte + TypeScript)
│   ├── App.svelte           # Main layout grid
│   ├── components/          # LP, GP, Meta, Notes, ToDo sections
│   ├── lib/                 # API bridge + shared stores
│   ├── styles/              # CSS grid and theme
│   └── vite-env.d.ts
│
├── src-tauri/
│   ├── src/main.rs          # Launches Python backend and Tauri window
│   ├── tauri.conf.json
│   └── python/              # Embedded backend
│       ├── backend.py       # FastAPI app entrypoint
│       ├── audio_service.py # Audio record/stop (stubbed)
│       ├── transcription_service.py
│       ├── summarization_agent.py
│       ├── database.py      # SQLModel ORM
│       ├── schema.sql       # DB initialization
│       └── requirements.txt
│
├── db/
│   └── crm.db               # SQLite file (auto-created)
│
├── data/
│   ├── recordings/          # .wav/.mp3 files
│   ├── transcripts/         # Whisper output
│   └── summaries/           # Ollama summaries
│
├── setup/
│   ├── install.sh           # macOS installer
│   └── setup.py             # Python DB initializer
├── package.json
├── requirements.txt
└── DEVELOPER_NOTES.md       # You are here
```

---

## 🧩 Core Concepts

### 1. Frontend

Built with **Svelte + TypeScript** and rendered through Tauri's WebView.
All business logic and data writes happen through the backend; the UI is stateless and replaceable (e.g., React later).

**Frontend responsibilities:**
- Display forms and notes UI
- Invoke backend commands using `@tauri-apps/api/tauri.invoke()`
- Maintain session state in `stores.ts`

---

### 2. Backend

Runs as an embedded **FastAPI** server under `src-tauri/python/backend.py`.

**Key modules:**

| File | Role |
|------|------|
| `audio_service.py` | Records microphone/system audio. Stubs now; connects to CoreAudio later. |
| `transcription_service.py` | Runs Whisper CPP locally and returns transcript path. |
| `summarization_agent.py` | Calls Ollama to summarize transcripts and notes. |
| `database.py` | SQLModel ORM models + session helper. |
| `schema.sql` | Base schema for SQLite initialization. |

---

### 3. Database Layer

Currently **SQLite** for portability — stored in `/db/crm.db`.
Future migration to **PostgreSQL** uses the same SQLModel definitions.

**Tables include:**
- `lp`, `gp`, `person`, `note`, `todo`

**Each note links to:**
- One `lp`
- One `gp`
- Multiple `people`
- Optional `fundraise` stage
- Optional `interest` (sales funnel stage)

---

## 🧱 Development Tasks

### ▶️ Run locally

```bash
./setup/install.sh     # first-time setup
npm install
npm run tauri:dev
```

### 🧹 Clean rebuild

```bash
rm -rf db data
./setup/install.sh
```

---

## 🔧 Adding New Backend Endpoints

1. **Edit** `src-tauri/python/backend.py`

2. **Add route:**

```python
@app.post("/new-feature")
def new_feature(payload: dict):
    # do something
    return {"status": "ok"}
```

3. **Expose it to the frontend** via `src/lib/api.ts`:

```typescript
import { invoke } from "@tauri-apps/api";

export async function newFeature(data: any) {
  return await invoke("new_feature", { data });
}
```

---

## 🧩 Adding New Database Tables

1. **Define new SQLModel class** in `database.py`:

```python
class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    owner_id: Optional[int] = Field(default=None, foreign_key="person.id")
```

2. **Add CREATE TABLE** line in `schema.sql`

3. **Run** `python setup/setup.py` again or add migrations later with Alembic

---

## 🧠 Integrating Whisper CPP

To activate transcription:

1. **Place** your main Whisper CPP binary in `/usr/local/bin/`

2. **Update** `transcription_service.py`:

```python
subprocess.run([
    "whisper",
    input_file,
    "--model", "base",
    "--output_dir", "data/transcripts"
])
```

3. **Store** the resulting text path in the database

---

## 🤖 Integrating Ollama

After Whisper works, connect to your Ollama server:

```python
import requests

def summarize(transcript_text):
    res = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "mistral", "prompt": transcript_text}
    )
    return res.json()["response"]
```

Store the result in `/data/summaries/meeting_<id>.json`

---

## 🧩 Linking Interest → Sales Funnel

Interest dropdown in `MeetingMeta.svelte` maps directly to the sales funnel concept.

**Stages:**
```
["New Contact", "Early Interest", "Active Diligence", "Soft Commit", "Closed"]
```

These populate automatically from the database on app start.

---

## 🧰 Migrating to PostgreSQL

1. **Change** `DATABASE_URL` in `database.py`:

```python
DATABASE_URL = "postgresql://user:pass@localhost:5432/meetingapp"
```

2. **Re-run** schema creation

3. The rest of your app (FastAPI routes, UI) **works without change**

---

## 🪜 Deployment Notes

- Build with `npm run tauri:build` to package a `.app` for macOS
- Python runtime and dependencies are bundled under `/src-tauri/python/lib/`
- On first launch, the app runs `setup.py` automatically if `crm.db` is missing
- Keep Whisper CPP and Ollama on the same system or reachable over LAN

---

## 🧠 Future Modules (To Be Added)

| Module | Description |
|--------|-------------|
| `environment_check.py` | Verify Whisper/Ollama availability |
| `sync_service.py` | Push/pull data between local and office server |
| `embedding_agent.py` | Vectorize notes for semantic search |
| `scheduler.py` | Auto-scan transcripts and remind follow-ups |

---

## 💡 Developer Tips

- Use `console.log` in Svelte and `print()` in Python; both logs show in Tauri console
- Avoid hardcoding paths; use `os.path.join()` for cross-platform safety
- Keep frontend stateless — everything should be reproducible from DB data
- Test backend endpoints independently using `curl` or Postman before UI integration
- Use `sqlite3 db/crm.db` for quick database inspection during development

---

## 🔍 Debugging Guide

### Frontend Issues

**Check browser console:**
```bash
# In Tauri dev mode, press F12 or Cmd+Option+I
# Look for errors in Console tab
```

**Check stores:**
```javascript
// In browser console
window.$lps  // View LP store
window.$notes  // View notes store
```

### Backend Issues

**Check FastAPI logs:**
```bash
# Backend logs appear in terminal running backend.py
# Look for traceback or HTTP status codes
```

**Test endpoints directly:**
```bash
curl http://localhost:8000/health
curl http://localhost:8000/lps
```

**View API docs:**
```bash
open http://localhost:8000/docs
```

### Database Issues

**Inspect database:**
```bash
sqlite3 db/crm.db
.tables
.schema note
SELECT * FROM note;
.quit
```

**Reset database:**
```bash
rm db/crm.db
python setup/setup.py
```

---

## 📋 Change Log

| Version | Date | Description |
|---------|------|-------------|
| 0.1 | 2025-10-24 | Initial scaffold — Full layout, portable backend, setup automation |

---

## 🔐 Security Notes

- Database is local-only (no network exposure by default)
- Audio recordings contain sensitive conversations — ensure proper file permissions
- When migrating to PostgreSQL, use environment variables for credentials
- Never commit `db/crm.db` or `data/` directories to version control (covered in `.gitignore`)

---

## 🧪 Testing Strategy

### Unit Tests (Future)
```bash
# Backend
pytest src-tauri/python/tests/

# Frontend
npm run test
```

### Integration Tests
```bash
# Test full workflow
1. Create LP/GP via UI
2. Record meeting (stub)
3. Add notes
4. Generate todos
5. Verify database entries
```

### Manual Testing Checklist
- [ ] LP/GP creation and selection
- [ ] Meeting metadata (date, fundraise, interest)
- [ ] Notes editor with auto-save
- [ ] Todo creation and status toggle
- [ ] History view shows all notes
- [ ] Contacts view shows all LPs/GPs

---

## 📚 Additional Resources

- [Tauri Documentation](https://tauri.app)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com)
- [Svelte Documentation](https://svelte.dev)
- [Whisper CPP](https://github.com/ggerganov/whisper.cpp)
- [Ollama](https://ollama.ai)

---

**Last Updated**: 2025-10-24
**Maintainer**: Louis Viramontes
**Status**: Active Development
