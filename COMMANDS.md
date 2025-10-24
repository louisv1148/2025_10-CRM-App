# Quick Command Reference

## 🚀 Development Commands

### Start Development

```bash
# Full setup (first time only)
./setup/install.sh

# Start backend API
source src-tauri/python/lib/bin/activate
python3 src-tauri/python/backend.py

# Or use npm script
npm run backend

# Start Tauri app (in another terminal)
npm run tauri:dev
```

### Frontend Only

```bash
# Vite dev server only (no Tauri)
npm run dev

# Opens http://localhost:1420 in browser
```

---

## 🗄️ Database Commands

### Initialize Database

```bash
# Create database with schema and seed data
python3 setup/setup.py

# Or use npm script
npm run db:init
```

### View Database

```bash
# Open SQLite CLI
sqlite3 db/crm.db

# Or use npm script
npm run db:view
```

### Useful SQLite Commands

```sql
-- List all tables
.tables

-- Show table schema
.schema note

-- View data
SELECT * FROM lp;
SELECT * FROM gp;
SELECT * FROM note;
SELECT * FROM todo;

-- Count records
SELECT COUNT(*) FROM note;

-- Recent notes
SELECT id, date, summary FROM note ORDER BY date DESC LIMIT 10;

-- Exit
.quit
```

### Reset Database

```bash
# Delete and recreate
rm db/crm.db
python3 setup/setup.py
```

---

## 🧪 Testing Commands

### Backend API Tests

```bash
# Health check
curl http://localhost:8000/health

# List LPs
curl http://localhost:8000/lps

# List GPs
curl http://localhost:8000/gps

# List Notes
curl http://localhost:8000/notes

# List Todos
curl http://localhost:8000/todos

# Create new LP
curl -X POST http://localhost:8000/lps \
  -H "Content-Type: application/json" \
  -d '{"name":"New Fund"}'

# API documentation (Swagger)
open http://localhost:8000/docs
```

### Check Running Processes

```bash
# Check if backend is running
lsof -i :8000

# Check Python processes
ps aux | grep backend.py

# Kill backend process
pkill -f backend.py
```

---

## 📦 Build Commands

### Production Build

```bash
# Build frontend
npm run build

# Build Tauri app (creates .app, .dmg)
npm run tauri:build

# Output location
ls src-tauri/target/release/bundle/
```

---

## 🔧 Maintenance Commands

### Update Dependencies

```bash
# Python
source src-tauri/python/lib/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --upgrade

# Node
npm update
npm audit fix
```

### Clean Build

```bash
# Remove build artifacts
rm -rf node_modules
rm -rf src-tauri/target
rm -rf dist

# Clean database and data
rm -rf db data

# Reinstall
npm install
./setup/install.sh
```

---

## 🐛 Debug Commands

### View Logs

```bash
# Backend logs (while running)
# Appears in terminal where backend.py is running

# Tauri logs
# Appears in terminal where npm run tauri:dev is running

# Frontend logs
# Open DevTools in Tauri window (F12 or Cmd+Option+I)
```

### Test Audio Devices

```bash
source src-tauri/python/lib/bin/activate
python3 src-tauri/python/audio_service.py
```

### Test AI Services

```bash
# Test transcription service
source src-tauri/python/lib/bin/activate
python3 src-tauri/python/transcription_service.py

# Test summarization agent
python3 src-tauri/python/summarization_agent.py
```

---

## 📝 Git Commands

### Common Workflow

```bash
# Check status
git status

# Add files
git add .

# Commit
git commit -m "Your message"

# Push to GitHub
git push origin master

# Pull latest
git pull origin master
```

### View History

```bash
# Recent commits
git log --oneline -10

# Show changes
git diff

# Show last commit
git show
```

---

## 🔍 Inspection Commands

### Project Structure

```bash
# View directory tree (if tree installed)
tree -L 3 -I 'node_modules|target|venv|__pycache__'

# Count files
find . -type f | wc -l

# Count lines of code
find src -name "*.svelte" -o -name "*.ts" | xargs wc -l
find src-tauri/python -name "*.py" | xargs wc -l
```

### Check Installation

```bash
# Check versions
python3 --version
node --version
cargo --version
npm --version

# Check venv packages
source src-tauri/python/lib/bin/activate
pip list

# Check node packages
npm list --depth=0
```

---

## 🛠️ Troubleshooting Commands

### Port Already in Use

```bash
# Find process on port 8000
lsof -i :8000

# Kill it
kill -9 <PID>
```

### PyAudio Issues

```bash
# Install PortAudio
brew install portaudio

# Reinstall PyAudio
source src-tauri/python/lib/bin/activate
pip uninstall pyaudio
pip install pyaudio
```

### Rust/Cargo Issues

```bash
# Add to PATH
source "$HOME/.cargo/env"

# Update Rust
rustup update

# Clean Rust build
cd src-tauri
cargo clean
```

### Database Locked

```bash
# Check for lock file
ls -la db/

# Remove lock
rm db/crm.db-journal

# Restart backend
pkill -f backend.py
npm run backend
```

---

## 📊 Quick Stats

```bash
# Show project stats
echo "Files: $(find . -type f | wc -l)"
echo "Code lines: $(find src src-tauri/python -name '*.py' -o -name '*.ts' -o -name '*.svelte' | xargs wc -l | tail -1)"
echo "Database size: $(ls -lh db/crm.db | awk '{print $5}')"
echo "Recordings: $(ls data/recordings | wc -l)"
```

---

## 🎯 One-Liners

```bash
# Full restart
pkill -f backend.py && npm run backend & npm run tauri:dev

# Quick test
curl -s http://localhost:8000/health | python3 -m json.tool

# View latest note
sqlite3 db/crm.db "SELECT * FROM note ORDER BY date DESC LIMIT 1;"

# Count todos
sqlite3 db/crm.db "SELECT COUNT(*) FROM todo WHERE status='pending';"

# Backup database
cp db/crm.db db/crm_backup_$(date +%Y%m%d).db
```

---

**Tip**: Add these to your shell aliases for faster access!

```bash
# Add to ~/.zshrc or ~/.bashrc
alias crm-dev="cd '/Users/lvc/AI Scripts/2025_10 CRM App' && npm run tauri:dev"
alias crm-backend="cd '/Users/lvc/AI Scripts/2025_10 CRM App' && npm run backend"
alias crm-db="sqlite3 '/Users/lvc/AI Scripts/2025_10 CRM App/db/crm.db'"
```
