-- Database schema for CRM Meeting App
-- This file is for reference; SQLModel will auto-create tables
-- Use this for manual migrations if needed

-- Limited Partners table
CREATE TABLE IF NOT EXISTS lp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_lp_name ON lp(name);

-- General Partners table
CREATE TABLE IF NOT EXISTS gp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_gp_name ON gp(name);

-- People/Contacts table
CREATE TABLE IF NOT EXISTS person (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    org_type TEXT NOT NULL,  -- LP/GP/Other
    org_id INTEGER,
    email TEXT,
    phone TEXT
);

CREATE INDEX IF NOT EXISTS idx_person_org ON person(org_type, org_id);

-- Meeting Notes table
CREATE TABLE IF NOT EXISTS note (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    lp_id INTEGER,
    gp_id INTEGER,
    raw_notes TEXT DEFAULT '',
    summary TEXT DEFAULT '',
    fundraise TEXT,
    interest TEXT,
    audio_path TEXT,
    transcription_path TEXT,
    FOREIGN KEY (lp_id) REFERENCES lp(id) ON DELETE SET NULL,
    FOREIGN KEY (gp_id) REFERENCES gp(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_note_date ON note(date DESC);
CREATE INDEX IF NOT EXISTS idx_note_lp ON note(lp_id);
CREATE INDEX IF NOT EXISTS idx_note_gp ON note(gp_id);

-- Todos/Action Items table
CREATE TABLE IF NOT EXISTS todo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    note_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    status TEXT DEFAULT 'pending',  -- pending/completed
    due_date TIMESTAMP,
    FOREIGN KEY (note_id) REFERENCES note(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_todo_note ON todo(note_id);
CREATE INDEX IF NOT EXISTS idx_todo_status ON todo(status);
