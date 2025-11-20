# CRM Cloud Migration Architecture

## Overview

Migration from local SQLite/Tauri desktop app to cloud-based AWS infrastructure with PostgreSQL (RDS), Qdrant vector search, and FastAPI backend.

---

## Current Stack → Target Stack

| Component | Local (Current) | Cloud (Target) |
|-----------|-----------------|----------------|
| Database | SQLite (`db/crm.db`) | PostgreSQL (RDS t3.micro) |
| Vector DB | None | Qdrant Cloud |
| Backend | FastAPI (localhost:8000) | FastAPI (EC2/ECS) |
| Frontend | Tauri + Svelte | Web (S3/CloudFront) or Tauri hybrid |
| File Storage | Local filesystem | S3 |
| AI Processing | Local Python | EC2 (GPU for Whisper) |

---

## What Works Already

### 1. Database Migration (SQLite → PostgreSQL)

Your current setup in `src-tauri/python/database.py`:
```python
DB_PATH = os.path.join(os.path.dirname(__file__), "../../db/crm.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL, echo=True)
```

**Why it's easy:** SQLModel/SQLAlchemy abstracts the database engine. Your models (LP, GP, Note, Todo, Fund, Roadshow, Person, etc.) don't need changes - only the connection string changes.

**Target:**
```python
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://crm:password@your-rds-endpoint:5432/crm_core"
)
```

### 2. AI Pipeline Services

Your existing services align with cloud architecture:

- `audio_service.py` - Recording → S3 upload
- `transcription_service.py` - Whisper → EC2 GPU instance
- `summarization_agent.py` - LLM summarization → Lambda or EC2

### 3. Frontend API Integration

`src/lib/api.ts` already uses fetch() calls with consistent patterns:
- Configurable `baseURL` is straightforward
- No structural changes needed
- CORS configuration on FastAPI side is the main work

### 4. Docker Compose (Local Dev)

```yaml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: crm
      POSTGRES_PASSWORD: securepassword
      POSTGRES_DB: crm_core
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U crm"]
      interval: 5s
      timeout: 5s
      retries: 5

  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  api:
    build: ./src-tauri/python
    depends_on:
      db:
        condition: service_healthy
      qdrant:
        condition: service_started
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://crm:securepassword@db:5432/crm_core
      - QDRANT_URL=http://qdrant:6333

volumes:
  pgdata:
  qdrant_data:
```

---

## Things to Add

### 1. Configuration File (`config.py`)

**Location:** `src-tauri/python/config.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./db/crm.db"  # Fallback for local dev
)

# Qdrant Vector DB
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")

# AWS S3
S3_BUCKET = os.getenv("S3_BUCKET", "")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Frontend URL (for CORS)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# API Settings
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "8000"))
```

### 2. Environment File (`.env.example`)

```bash
# Database
DATABASE_URL=postgresql://crm:password@localhost:5432/crm_core

# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=

# AWS
S3_BUCKET=crm-audio-files
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

# Frontend
FRONTEND_URL=http://localhost:5173

# API
API_HOST=0.0.0.0
API_PORT=8000
```

### 3. Data Migration Script

**Location:** `src-tauri/python/migrate_to_postgres.py`

Needed for:
- Export existing SQLite data
- Import into PostgreSQL
- Handle datetime/type differences between SQLite and Postgres
- Preserve all relationships (link tables)

### 4. Qdrant Embedding Pipeline

Not yet implemented. Required components:
- Embedding generator (OpenAI, Sentence Transformers)
- Collection creation for notes
- Sync mechanism between PostgreSQL and Qdrant
- Search endpoint in backend

### 5. Authentication Layer

For cloud deployment, you'll need:
- JWT token generation/validation
- Route protection in FastAPI
- Token storage in `stores.ts`
- Options: AWS Cognito, Auth0, or custom

### 6. Tauri → Web Strategy

**Options:**
1. **Keep Tauri** - Local-first with cloud API fallback
2. **Full Web** - SvelteKit with PWA capabilities
3. **Hybrid** - Tauri for desktop, web for mobile/remote

---

## File Changes Required

| File | Change Type | Complexity | Details |
|------|-------------|------------|---------|
| `database.py` | Connection string → env var | Low | Use `config.py` import |
| `backend.py` | Add config imports, Qdrant client, CORS | Medium | ~20 lines at top |
| `api.ts` | Configurable baseURL | Low | Environment variable |
| `stores.ts` | Auth token handling | Medium | Only if adding auth |
| `App.svelte` | Minimal changes | Low | Already routing correctly |

---

## Backend Modifications

### Update `backend.py` Top Section

```python
# At top of backend.py
from dotenv import load_dotenv
import os
from qdrant_client import QdrantClient

load_dotenv()

# Import config
from config import FRONTEND_URL, QDRANT_URL, QDRANT_API_KEY

# Update CORS origins
origins = [
    FRONTEND_URL,
    "http://localhost:5173",  # Keep for local dev
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Qdrant client (optional - enable when needed)
if QDRANT_URL:
    qdrant_client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY if QDRANT_API_KEY else None
    )
else:
    qdrant_client = None
```

### Update `database.py` Engine Creation

```python
from config import DATABASE_URL

# Remove hardcoded path
engine = create_engine(DATABASE_URL, echo=True)
```

---

## Migration Phases

| Phase | Task | Priority | Status |
|-------|------|----------|--------|
| 1 | Create `config.py` with environment variables | High | Pending |
| 2 | Create `.env` and `.env.example` files | High | Pending |
| 3 | Update `database.py` to use config | High | Pending |
| 4 | Update `backend.py` with CORS and config | High | Pending |
| 5 | Create Docker Compose for local Postgres/Qdrant | Medium | Pending |
| 6 | Build SQLite → PostgreSQL migration script | High | Pending |
| 7 | Update `api.ts` with configurable baseURL | Medium | Pending |
| 8 | Implement Qdrant embedding pipeline | Medium | Pending |
| 9 | Add authentication layer | High | Pending |
| 10 | Deploy to AWS (RDS, EC2, S3) | Medium | Pending |
| 11 | Address Tauri/Web deployment strategy | Medium | Pending |

---

## AWS Cost Optimization

| Service | Instance/Tier | Estimated Monthly Cost |
|---------|---------------|------------------------|
| RDS PostgreSQL | t3.micro (free tier eligible) | $0-15 |
| EC2 (API) | t3.micro or spot | $5-10 |
| EC2 (GPU for Whisper) | On-demand when needed | Pay per use |
| S3 | Standard | ~$0.023/GB |
| Qdrant Cloud | Free tier (1GB) | $0 |
| **Total** | | **~$20-40/month** |

---

## Key Files Reference

### Backend
- `src-tauri/python/backend.py` - FastAPI endpoints (1200+ lines)
- `src-tauri/python/database.py` - SQLModel models and engine
- `src-tauri/python/audio_service.py` - Audio recording
- `src-tauri/python/transcription_service.py` - Whisper transcription
- `src-tauri/python/summarization_agent.py` - LLM summarization

### Frontend
- `src/lib/api.ts` - All fetch functions
- `src/lib/stores.ts` - Svelte state management
- `src/App.svelte` - Main app routing

### Models (in database.py)
- LP, GP, Fund, Note, Todo, Person, Roadshow
- Link tables: NoteLPLink, NoteGPLink, TodoLPLink, etc.
- Status tables: FundLPInterest, RoadshowLPStatus

---

## Conclusion

The migration plan is **sound and low-risk** because:

1. **SQLModel abstraction** - Database models are portable
2. **Clean API layer** - Frontend already uses fetch()
3. **Phased approach** - Can migrate incrementally
4. **Cost-effective** - AWS free tier covers most needs initially

### Immediate Next Steps

1. Create `config.py` and `.env` files
2. Test with local Docker Postgres (before touching production)
3. Build migration script and test with copy of data
4. Deploy API to EC2, update frontend baseURL
5. Add Qdrant for semantic search later

### Dependencies to Install

```bash
pip install python-dotenv psycopg2-binary qdrant-client
```

---

*Last updated: November 2024*
*Generated for CRM Meeting App cloud migration*
