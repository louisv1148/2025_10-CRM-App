"""
FastAPI backend for CRM application
Provides REST API endpoints for Tauri frontend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os

from database import (
    LP, GP, Person, Note, Todo, Distributor, Fund,
    GPLPLink, GPPersonLink, LPPersonLink, DistributorPersonLink,
    NoteLPLink, NoteGPLink, NoteFundLink,
    get_session, create_db_and_tables
)

app = FastAPI(title="CRM Backend API")

# CORS middleware for Tauri
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tauri app origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory for notion images
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "notion_images")
if os.path.exists(IMAGES_DIR):
    app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")

# Startup event
@app.on_event("startup")
async def startup():
    create_db_and_tables()


# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


# LP endpoints
@app.get("/lps", response_model=List[LP])
async def get_lps():
    """Get all LPs"""
    with get_session() as session:
        lps = session.query(LP).all()
        return lps


@app.post("/lps", response_model=LP)
async def create_lp(lp: LP):
    """Create new LP"""
    with get_session() as session:
        session.add(lp)
        session.commit()
        session.refresh(lp)
        return lp


@app.put("/lps/{lp_id}")
async def update_lp(lp_id: int, lp_update: LP):
    """Update LP"""
    with get_session() as session:
        lp = session.get(LP, lp_id)
        if not lp:
            raise HTTPException(status_code=404, detail="LP not found")

        # Update fields
        for key, value in lp_update.dict(exclude_unset=True).items():
            if key != "id":  # Don't update the ID
                setattr(lp, key, value)

        session.add(lp)
        session.commit()
        session.refresh(lp)
        return lp


@app.delete("/lps/{lp_id}")
async def delete_lp(lp_id: int):
    """Delete LP"""
    with get_session() as session:
        lp = session.get(LP, lp_id)
        if not lp:
            raise HTTPException(status_code=404, detail="LP not found")
        session.delete(lp)
        session.commit()
        return {"status": "deleted"}


@app.get("/lps/search", response_model=List[LP])
async def search_lps(q: str = ""):
    """Search LPs by name"""
    with get_session() as session:
        if not q or len(q.strip()) == 0:
            return []
        query = session.query(LP).filter(LP.name.ilike(f"%{q}%")).limit(10)
        return query.all()


# GP endpoints
@app.get("/gps", response_model=List[GP])
async def get_gps():
    """Get all GPs"""
    with get_session() as session:
        gps = session.query(GP).all()
        return gps


@app.post("/gps", response_model=GP)
async def create_gp(gp: GP):
    """Create new GP"""
    with get_session() as session:
        session.add(gp)
        session.commit()
        session.refresh(gp)
        return gp


@app.put("/gps/{gp_id}")
async def update_gp(gp_id: int, gp_update: GP):
    """Update GP"""
    with get_session() as session:
        gp = session.get(GP, gp_id)
        if not gp:
            raise HTTPException(status_code=404, detail="GP not found")

        # Update fields
        for key, value in gp_update.dict(exclude_unset=True).items():
            if key != "id":  # Don't update the ID
                setattr(gp, key, value)

        session.add(gp)
        session.commit()
        session.refresh(gp)
        return gp

@app.delete("/gps/{gp_id}")
async def delete_gp(gp_id: int):
    """Delete GP"""
    with get_session() as session:
        gp = session.get(GP, gp_id)
        if not gp:
            raise HTTPException(status_code=404, detail="GP not found")
        session.delete(gp)
        session.commit()
        return {"status": "deleted"}


@app.get("/gps/search", response_model=List[GP])
async def search_gps(q: str = ""):
    """Search GPs by name"""
    with get_session() as session:
        if not q or len(q.strip()) == 0:
            return []
        query = session.query(GP).filter(GP.name.ilike(f"%{q}%")).limit(10)
        return query.all()


# Distributor endpoints
@app.get("/distributors", response_model=List[Distributor])
async def get_distributors():
    """Get all Distributors"""
    with get_session() as session:
        distributors = session.query(Distributor).all()
        return distributors


@app.post("/distributors", response_model=Distributor)
async def create_distributor(distributor: Distributor):
    """Create new Distributor"""
    with get_session() as session:
        session.add(distributor)
        session.commit()
        session.refresh(distributor)
        return distributor


# Fund endpoints
@app.get("/funds", response_model=List[Fund])
async def get_funds():
    """Get all funds"""
    with get_session() as session:
        funds = session.query(Fund).order_by(Fund.fund_name).all()
        return funds


@app.get("/funds/search", response_model=List[Fund])
async def search_funds(q: str = ""):
    """Search funds by name"""
    with get_session() as session:
        if not q or len(q.strip()) == 0:
            return []
        query = session.query(Fund).filter(Fund.fund_name.ilike(f"%{q}%")).limit(10)
        return query.all()


# Person endpoints
@app.get("/people", response_model=List[Person])
async def get_people():
    """Get all people"""
    with get_session() as session:
        people = session.query(Person).all()
        return people


@app.post("/people", response_model=Person)
async def create_person(person: Person):
    """Create new person"""
    with get_session() as session:
        session.add(person)
        session.commit()
        session.refresh(person)
        return person


@app.put("/people/{person_id}")
async def update_person(person_id: int, person_update: Person):
    """Update person"""
    with get_session() as session:
        person = session.get(Person, person_id)
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")

        # Update fields
        for key, value in person_update.dict(exclude_unset=True).items():
            if key != "id":  # Don't update the ID
                setattr(person, key, value)

        session.add(person)
        session.commit()
        session.refresh(person)
        return person


@app.get("/people/search", response_model=List[Person])
async def search_people(q: str = ""):
    """Search people by name"""
    with get_session() as session:
        if not q or len(q.strip()) == 0:
            return []
        query = session.query(Person).filter(Person.name.ilike(f"%{q}%")).limit(10)
        return query.all()


# Note endpoints
@app.get("/notes", response_model=List[Note])
async def get_notes():
    """Get all notes"""
    with get_session() as session:
        notes = session.query(Note).order_by(Note.date.desc()).all()
        return notes


@app.get("/notes/{note_id}", response_model=Note)
async def get_note(note_id: int):
    """Get specific note"""
    with get_session() as session:
        note = session.get(Note, note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return note


@app.get("/notes/{note_id}/lps")
async def get_note_lps(note_id: int):
    """Get all LPs associated with a note"""
    with get_session() as session:
        links = session.query(NoteLPLink).filter(NoteLPLink.note_id == note_id).all()
        lp_ids = [link.lp_id for link in links]

        if not lp_ids:
            return []

        lps = session.query(LP).filter(LP.id.in_(lp_ids)).all()
        return lps


@app.get("/notes/{note_id}/gps")
async def get_note_gps(note_id: int):
    """Get all GPs associated with a note"""
    with get_session() as session:
        links = session.query(NoteGPLink).filter(NoteGPLink.note_id == note_id).all()
        gp_ids = [link.gp_id for link in links]

        if not gp_ids:
            return []

        gps = session.query(GP).filter(GP.id.in_(gp_ids)).all()
        return gps


@app.get("/notes/{note_id}/funds")
async def get_note_funds(note_id: int):
    """Get all funds associated with a note"""
    with get_session() as session:
        links = session.query(NoteFundLink).filter(NoteFundLink.note_id == note_id).all()
        fund_ids = [link.fund_id for link in links]

        if not fund_ids:
            return []

        funds = session.query(Fund).filter(Fund.id.in_(fund_ids)).all()
        return funds


@app.post("/notes", response_model=Note)
async def create_note(note: Note):
    """Create new note"""
    with get_session() as session:
        # Convert string date to datetime if needed
        if isinstance(note.date, str):
            try:
                note.date = datetime.fromisoformat(note.date)
            except (ValueError, AttributeError):
                note.date = None

        session.add(note)
        session.commit()
        session.refresh(note)
        return note


@app.put("/notes/{note_id}", response_model=Note)
async def update_note(note_id: int, note_update: Note):
    """Update existing note"""
    with get_session() as session:
        note = session.get(Note, note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")

        # Update fields
        update_dict = note_update.dict(exclude_unset=True)

        # Convert string date to datetime if needed
        if 'date' in update_dict and isinstance(update_dict['date'], str):
            try:
                update_dict['date'] = datetime.fromisoformat(update_dict['date'])
            except (ValueError, AttributeError):
                update_dict['date'] = None

        for key, value in update_dict.items():
            setattr(note, key, value)

        session.add(note)
        session.commit()
        session.refresh(note)
        return note


@app.post("/notes/{note_id}/relationships")
async def create_note_relationships(
    note_id: int,
    lp_ids: list[int] = [],
    gp_ids: list[int] = [],
    participant_ids: list[int] = [],
    fund_ids: list[int] = []
):
    """Create relationships between a note and LPs, GPs, participants, and funds"""
    with get_session() as session:
        # Verify note exists
        note = session.get(Note, note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")

        # Clear existing relationships first
        session.query(NoteLPLink).filter(NoteLPLink.note_id == note_id).delete()
        session.query(NoteGPLink).filter(NoteGPLink.note_id == note_id).delete()
        session.query(NoteFundLink).filter(NoteFundLink.note_id == note_id).delete()
        # Note: We don't have a NotePersonLink table, participants are linked via LP/GP

        # Create LP links
        for lp_id in lp_ids:
            link = NoteLPLink(note_id=note_id, lp_id=lp_id)
            session.add(link)

        # Create GP links
        for gp_id in gp_ids:
            link = NoteGPLink(note_id=note_id, gp_id=gp_id)
            session.add(link)

        # Create Fund links
        for fund_id in fund_ids:
            link = NoteFundLink(note_id=note_id, fund_id=fund_id)
            session.add(link)

        # For participants, we'll link them via LPPersonLink if they're associated with the selected LP
        # This is a simplification - ideally we'd have a NotePersonLink table

        session.commit()
        return {"success": True, "note_id": note_id}


# Todo endpoints
@app.get("/todos", response_model=List[Todo])
async def get_todos():
    """Get all todos"""
    with get_session() as session:
        todos = session.query(Todo).all()
        return todos


@app.post("/todos", response_model=Todo)
async def create_todo(todo: Todo):
    """Create new todo"""
    with get_session() as session:
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo


@app.put("/todos/{todo_id}", response_model=Todo)
async def update_todo(todo_id: int, todo_update: Todo):
    """Update todo (e.g., mark as completed)"""
    with get_session() as session:
        todo = session.get(Todo, todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")

        for key, value in todo_update.dict(exclude_unset=True).items():
            setattr(todo, key, value)

        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo


# Relationship endpoints
@app.get("/gps/{gp_id}/people")
async def get_gp_people(gp_id: int):
    """Get all people associated with a GP"""
    with get_session() as session:
        # Query people through the link table
        links = session.query(GPPersonLink).filter(GPPersonLink.gp_id == gp_id).all()
        person_ids = [link.person_id for link in links]

        if not person_ids:
            return []

        people = session.query(Person).filter(Person.id.in_(person_ids)).all()
        return people


@app.get("/lps/{lp_id}/people")
async def get_lp_people(lp_id: int):
    """Get all people associated with an LP"""
    with get_session() as session:
        # Query people through the link table
        links = session.query(LPPersonLink).filter(LPPersonLink.lp_id == lp_id).all()
        person_ids = [link.person_id for link in links]

        if not person_ids:
            return []

        people = session.query(Person).filter(Person.id.in_(person_ids)).all()
        return people


@app.get("/people/{person_id}/gps")
async def get_person_gps(person_id: int):
    """Get all GPs associated with a person"""
    with get_session() as session:
        # Query GPs through the link table
        links = session.query(GPPersonLink).filter(GPPersonLink.person_id == person_id).all()
        gp_ids = [link.gp_id for link in links]

        if not gp_ids:
            return []

        gps = session.query(GP).filter(GP.id.in_(gp_ids)).all()
        return gps


@app.get("/people/{person_id}/lps")
async def get_person_lps(person_id: int):
    """Get all LPs associated with a person"""
    with get_session() as session:
        # Query LPs through the link table
        links = session.query(LPPersonLink).filter(LPPersonLink.person_id == person_id).all()
        lp_ids = [link.lp_id for link in links]

        if not lp_ids:
            return []

        lps = session.query(LP).filter(LP.id.in_(lp_ids)).all()
        return lps


@app.get("/lps/{lp_id}/notes")
async def get_lp_notes(lp_id: int):
    """Get all notes associated with an LP"""
    with get_session() as session:
        # Query notes through the link table
        links = session.query(NoteLPLink).filter(NoteLPLink.lp_id == lp_id).all()
        note_ids = [link.note_id for link in links]

        if not note_ids:
            return []

        notes = session.query(Note).filter(Note.id.in_(note_ids)).order_by(Note.date.desc()).all()
        return notes


@app.get("/lps/{lp_id}/tasks")
async def get_lp_tasks(lp_id: int):
    """Get all tasks associated with an LP (through notes)"""
    with get_session() as session:
        # First get all notes associated with this LP
        links = session.query(NoteLPLink).filter(NoteLPLink.lp_id == lp_id).all()
        note_ids = [link.note_id for link in links]

        if not note_ids:
            return []

        # Then get all tasks associated with those notes
        tasks = session.query(Todo).filter(Todo.note_id.in_(note_ids)).all()
        return tasks


@app.get("/gps/{gp_id}/notes")
async def get_gp_notes(gp_id: int):
    """Get all notes associated with a GP"""
    with get_session() as session:
        # Query notes through the link table
        links = session.query(NoteGPLink).filter(NoteGPLink.gp_id == gp_id).all()
        note_ids = [link.note_id for link in links]

        if not note_ids:
            return []

        notes = session.query(Note).filter(Note.id.in_(note_ids)).order_by(Note.date.desc()).all()
        return notes


@app.get("/gps/{gp_id}/tasks")
async def get_gp_tasks(gp_id: int):
    """Get all tasks associated with a GP (through notes)"""
    with get_session() as session:
        # First get all notes associated with this GP
        links = session.query(NoteGPLink).filter(NoteGPLink.gp_id == gp_id).all()
        note_ids = [link.note_id for link in links]

        if not note_ids:
            return []

        # Then get all tasks associated with those notes
        tasks = session.query(Todo).filter(Todo.note_id.in_(note_ids)).all()
        return tasks


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
