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
    LP, GP, Person, Note, Todo, Distributor, Fund, Roadshow,
    GPLPLink, GPPersonLink, LPPersonLink, DistributorPersonLink,
    NoteLPLink, NoteGPLink, NoteFundLink, NoteRoadshowLink,
    TodoLPLink, TodoGPLink, TodoPersonLink, TodoFundLink, TodoRoadshowLink, TodoNoteLink,
    FundLPInterest, RoadshowLPStatus,
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


@app.put("/distributors/{distributor_id}")
async def update_distributor(distributor_id: int, distributor_update: Distributor):
    """Update distributor"""
    with get_session() as session:
        distributor = session.get(Distributor, distributor_id)
        if not distributor:
            raise HTTPException(status_code=404, detail="Distributor not found")

        # Update fields
        for key, value in distributor_update.dict(exclude_unset=True).items():
            if key != "id":  # Don't update the ID
                setattr(distributor, key, value)

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


@app.post("/funds", response_model=Fund)
async def create_fund(fund: Fund):
    """Create new fund"""
    with get_session() as session:
        # Convert date strings and empty strings to proper datetime objects or None
        date_fields = ['launch', 'final_close', 'roadshow_date']
        for field in date_fields:
            if hasattr(fund, field):
                value = getattr(fund, field)
                if value == '' or value is None:
                    setattr(fund, field, None)
                elif isinstance(value, str):
                    try:
                        from datetime import datetime
                        setattr(fund, field, datetime.fromisoformat(value))
                    except (ValueError, AttributeError):
                        setattr(fund, field, None)

        session.add(fund)
        session.commit()
        session.refresh(fund)
        return fund


@app.get("/funds/search", response_model=List[Fund])
async def search_funds(q: str = ""):
    """Search funds by name"""
    with get_session() as session:
        if not q or len(q.strip()) == 0:
            return []
        query = session.query(Fund).filter(Fund.fund_name.ilike(f"%{q}%")).limit(10)
        return query.all()


@app.get("/funds/{fund_id}/notes")
async def get_fund_notes(fund_id: int):
    """Get all notes associated with a fund"""
    with get_session() as session:
        # Query notes through the link table
        links = session.query(NoteFundLink).filter(NoteFundLink.fund_id == fund_id).all()
        note_ids = [link.note_id for link in links]

        if not note_ids:
            return []

        notes = session.query(Note).filter(Note.id.in_(note_ids)).order_by(Note.date.desc()).all()
        return notes


@app.put("/funds/{fund_id}")
async def update_fund(fund_id: int, fund_update: Fund):
    """Update fund"""
    with get_session() as session:
        fund = session.get(Fund, fund_id)
        if not fund:
            raise HTTPException(status_code=404, detail="Fund not found")

        # Update fields
        for key, value in fund_update.dict(exclude_unset=True).items():
            if key != 'id' and hasattr(fund, key):
                # Convert date strings and empty strings to proper datetime objects or None
                if key in ['launch', 'final_close', 'roadshow_date']:
                    if value == '' or value is None:
                        value = None
                    elif isinstance(value, str):
                        try:
                            from datetime import datetime
                            value = datetime.fromisoformat(value)
                        except (ValueError, AttributeError):
                            value = None
                setattr(fund, key, value)

        session.commit()
        session.refresh(fund)
        return fund


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


@app.post("/notes/{note_id}/funds/{fund_id}")
async def link_note_to_fund(note_id: int, fund_id: int):
    """Link a note to a fund"""
    with get_session() as session:
        # Check if link already exists
        existing = session.query(NoteFundLink).filter(
            NoteFundLink.note_id == note_id,
            NoteFundLink.fund_id == fund_id
        ).first()

        if existing:
            return {"success": True, "message": "Link already exists"}

        # Create new link
        link = NoteFundLink(note_id=note_id, fund_id=fund_id)
        session.add(link)
        session.commit()
        return {"success": True, "message": "Fund linked to note"}


@app.delete("/notes/{note_id}/funds/{fund_id}")
async def unlink_note_from_fund(note_id: int, fund_id: int):
    """Unlink a note from a fund"""
    with get_session() as session:
        session.query(NoteFundLink).filter(
            NoteFundLink.note_id == note_id,
            NoteFundLink.fund_id == fund_id
        ).delete()
        session.commit()
        return {"success": True, "message": "Fund unlinked from note"}


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


# Enhanced Todo endpoints with relationships and recurrence
@app.get("/todos", response_model=List[Todo])
async def get_todos(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    tag: Optional[str] = None,
    due_before: Optional[str] = None,
    due_after: Optional[str] = None
):
    """Get all todos with optional filtering"""
    with get_session() as session:
        query = session.query(Todo)

        if status:
            query = query.filter(Todo.status == status)
        if priority:
            query = query.filter(Todo.priority == priority)
        if tag:
            query = query.filter(Todo.tags.like(f"%{tag}%"))
        if due_before:
            query = query.filter(Todo.due_date <= due_before)
        if due_after:
            query = query.filter(Todo.due_date >= due_after)

        todos = query.order_by(Todo.due_date.asc(), Todo.priority.desc()).all()
        return todos


@app.post("/todos", response_model=Todo)
async def create_todo(todo: Todo):
    """Create new todo with optional relationships"""
    import json
    from datetime import timedelta, datetime as dt

    with get_session() as session:
        # Convert string dates to datetime objects
        if isinstance(todo.due_date, str):
            try:
                todo.due_date = dt.fromisoformat(todo.due_date)
            except (ValueError, AttributeError):
                todo.due_date = None

        session.add(todo)
        session.commit()
        session.refresh(todo)

        # Handle recurrence - create next instance if needed
        if todo.recurrence_pattern and not todo.parent_todo_id:
            try:
                pattern = json.loads(todo.recurrence_pattern)
                recurrence_type = pattern.get("type")
                interval = pattern.get("interval", 1)

                if recurrence_type and todo.due_date:
                    # Calculate next due date
                    if recurrence_type == "daily":
                        next_due = todo.due_date + timedelta(days=interval)
                    elif recurrence_type == "weekly":
                        next_due = todo.due_date + timedelta(weeks=interval)
                    elif recurrence_type == "monthly":
                        next_due = todo.due_date + timedelta(days=30 * interval)  # Approximate
                    else:
                        next_due = None

                    # Create next instance (will be created when current is completed)
                    # This is just a placeholder - actual creation happens on completion
            except:
                pass  # Invalid recurrence pattern, ignore

        return todo


@app.put("/todos/{todo_id}", response_model=Todo)
async def update_todo(todo_id: int, todo_update: Todo):
    """Update todo (e.g., mark as completed)"""
    import json
    from datetime import timedelta, datetime as dt

    with get_session() as session:
        todo = session.get(Todo, todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")

        update_data = todo_update.model_dump(exclude_unset=True)

        # Convert string dates to datetime objects
        if 'due_date' in update_data and isinstance(update_data['due_date'], str):
            try:
                update_data['due_date'] = dt.fromisoformat(update_data['due_date'])
            except (ValueError, AttributeError):
                update_data['due_date'] = None

        # If marking as completed and has recurrence, create next instance
        if update_data.get("status") == "completed" and todo.recurrence_pattern and not todo.parent_todo_id:
            try:
                pattern = json.loads(todo.recurrence_pattern)
                recurrence_type = pattern.get("type")
                interval = pattern.get("interval", 1)
                end_date_str = pattern.get("end_date")

                if recurrence_type and todo.due_date:
                    # Calculate next due date
                    if recurrence_type == "daily":
                        next_due = todo.due_date + timedelta(days=interval)
                    elif recurrence_type == "weekly":
                        next_due = todo.due_date + timedelta(weeks=interval)
                    elif recurrence_type == "monthly":
                        next_due = todo.due_date + timedelta(days=30 * interval)
                    else:
                        next_due = None

                    # Check if we should create next instance
                    should_create = True
                    if end_date_str and next_due:
                        end_date = dt.fromisoformat(end_date_str)
                        if next_due > end_date:
                            should_create = False

                    if should_create and next_due:
                        # Create next recurring instance
                        next_todo = Todo(
                            title=todo.title,
                            description=todo.description,
                            status="pending",
                            priority=todo.priority,
                            due_date=next_due,
                            recurrence_pattern=todo.recurrence_pattern,
                            parent_todo_id=todo.id,
                            tags=todo.tags,
                            note_id=todo.note_id
                        )
                        session.add(next_todo)
            except Exception as e:
                print(f"Error creating recurring todo: {e}")

        # Set completed_at if marking as completed
        if update_data.get("status") == "completed" and not update_data.get("completed_at"):
            update_data["completed_at"] = dt.utcnow()

        for key, value in update_data.items():
            setattr(todo, key, value)

        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo


@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    """Delete a todo"""
    with get_session() as session:
        todo = session.get(Todo, todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")

        session.delete(todo)
        session.commit()
        return {"success": True, "message": "Todo deleted"}


# Todo relationship endpoints
@app.post("/todos/{todo_id}/relationships")
async def create_todo_relationships(
    todo_id: int,
    lp_ids: List[int] = [],
    gp_ids: List[int] = [],
    person_ids: List[int] = [],
    fund_ids: List[int] = [],
    roadshow_ids: List[int] = [],
    note_ids: List[int] = []
):
    """Link a todo to LPs, GPs, People, Funds, Roadshows, and Notes"""
    with get_session() as session:
        todo = session.get(Todo, todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")

        # Clear existing relationships
        session.query(TodoLPLink).filter(TodoLPLink.todo_id == todo_id).delete()
        session.query(TodoGPLink).filter(TodoGPLink.todo_id == todo_id).delete()
        session.query(TodoPersonLink).filter(TodoPersonLink.todo_id == todo_id).delete()
        session.query(TodoFundLink).filter(TodoFundLink.todo_id == todo_id).delete()
        session.query(TodoRoadshowLink).filter(TodoRoadshowLink.todo_id == todo_id).delete()
        session.query(TodoNoteLink).filter(TodoNoteLink.todo_id == todo_id).delete()

        # Create new relationships
        for lp_id in lp_ids:
            session.add(TodoLPLink(todo_id=todo_id, lp_id=lp_id))
        for gp_id in gp_ids:
            session.add(TodoGPLink(todo_id=todo_id, gp_id=gp_id))
        for person_id in person_ids:
            session.add(TodoPersonLink(todo_id=todo_id, person_id=person_id))
        for fund_id in fund_ids:
            session.add(TodoFundLink(todo_id=todo_id, fund_id=fund_id))
        for roadshow_id in roadshow_ids:
            session.add(TodoRoadshowLink(todo_id=todo_id, roadshow_id=roadshow_id))
        for note_id in note_ids:
            session.add(TodoNoteLink(todo_id=todo_id, note_id=note_id))

        session.commit()
        return {"success": True, "todo_id": todo_id}


@app.get("/todos/{todo_id}/lps")
async def get_todo_lps(todo_id: int):
    """Get all LPs linked to a todo"""
    with get_session() as session:
        links = session.query(TodoLPLink).filter(TodoLPLink.todo_id == todo_id).all()
        lp_ids = [link.lp_id for link in links]
        lps = session.query(LP).filter(LP.id.in_(lp_ids)).all() if lp_ids else []
        return lps


@app.get("/todos/{todo_id}/gps")
async def get_todo_gps(todo_id: int):
    """Get all GPs linked to a todo"""
    with get_session() as session:
        links = session.query(TodoGPLink).filter(TodoGPLink.todo_id == todo_id).all()
        gp_ids = [link.gp_id for link in links]
        gps = session.query(GP).filter(GP.id.in_(gp_ids)).all() if gp_ids else []
        return gps


@app.get("/todos/{todo_id}/people")
async def get_todo_people(todo_id: int):
    """Get all people linked to a todo"""
    with get_session() as session:
        links = session.query(TodoPersonLink).filter(TodoPersonLink.todo_id == todo_id).all()
        person_ids = [link.person_id for link in links]
        people = session.query(Person).filter(Person.id.in_(person_ids)).all() if person_ids else []
        return people


@app.get("/todos/{todo_id}/funds")
async def get_todo_funds(todo_id: int):
    """Get all funds linked to a todo"""
    with get_session() as session:
        links = session.query(TodoFundLink).filter(TodoFundLink.todo_id == todo_id).all()
        fund_ids = [link.fund_id for link in links]
        funds = session.query(Fund).filter(Fund.id.in_(fund_ids)).all() if fund_ids else []
        return funds


@app.get("/todos/{todo_id}/roadshows")
async def get_todo_roadshows(todo_id: int):
    """Get all roadshows linked to a todo"""
    with get_session() as session:
        links = session.query(TodoRoadshowLink).filter(TodoRoadshowLink.todo_id == todo_id).all()
        roadshow_ids = [link.roadshow_id for link in links]
        roadshows = session.query(Roadshow).filter(Roadshow.id.in_(roadshow_ids)).all() if roadshow_ids else []
        return roadshows


@app.get("/todos/{todo_id}/notes")
async def get_todo_notes(todo_id: int):
    """Get all notes linked to a todo"""
    with get_session() as session:
        links = session.query(TodoNoteLink).filter(TodoNoteLink.todo_id == todo_id).all()
        note_ids = [link.note_id for link in links]
        notes = session.query(Note).filter(Note.id.in_(note_ids)).all() if note_ids else []
        return notes


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


# Sales Funnel endpoints
@app.get("/funds/{fund_id}/sales-funnel")
async def get_fund_sales_funnel(fund_id: int):
    """Get sales funnel for a fund with all LPs and their interest levels"""
    with get_session() as session:
        # Get all LPs
        all_lps = session.query(LP).all()

        # Get interest records for this fund
        interest_records = session.query(FundLPInterest).filter(
            FundLPInterest.fund_id == fund_id
        ).all()

        # Create a map of lp_id -> interest data
        interest_map = {record.lp_id: record for record in interest_records}

        # Build the sales funnel data
        result = []
        for lp in all_lps:
            interest_data = interest_map.get(lp.id)

            # Find the most recent note related to BOTH this LP and this fund
            # If no such note exists, leave the fields empty (None)
            latest_note = (
                session.query(Note)
                .join(NoteLPLink, Note.id == NoteLPLink.note_id)
                .join(NoteFundLink, Note.id == NoteFundLink.note_id)
                .filter(NoteLPLink.lp_id == lp.id)
                .filter(NoteFundLink.fund_id == fund_id)
                .order_by(Note.date.desc())
                .first()
            )

            # Extract note info (will be None if no note found)
            last_contact_date = latest_note.date if latest_note else None
            latest_note_id = latest_note.id if latest_note else None

            # Determine interest level
            interest_level = interest_data.interest if interest_data else "inactive"

            item = {
                "fund_id": fund_id,
                "lp_id": lp.id,
                "lp_name": lp.name,
                "interest": interest_level,
                "last_contact_date": last_contact_date.isoformat() if last_contact_date else None,
                "latest_note_id": latest_note_id,
                # LP details
                "aum_billions": lp.aum_billions,
                "location": lp.location,
                "priority": lp.priority,
                "advisor": lp.advisor,
                "type_of_group": lp.type_of_group,
                "investment_low": lp.investment_low,
                "investment_high": lp.investment_high,
            }

            result.append(item)

        return result


@app.put("/funds/{fund_id}/lps/{lp_id}/interest")
async def update_lp_interest(fund_id: int, lp_id: int, interest: str):
    """Update LP interest level for a fund"""
    with get_session() as session:
        # Check if record exists
        record = session.query(FundLPInterest).filter(
            FundLPInterest.fund_id == fund_id,
            FundLPInterest.lp_id == lp_id
        ).first()

        if record:
            # Update existing record
            record.interest = interest
        else:
            # Create new record
            record = FundLPInterest(fund_id=fund_id, lp_id=lp_id, interest=interest)
            session.add(record)

        # Update last_contact_date by finding the latest note related to both fund and LP
        # Get notes that are linked to both the fund and the LP
        fund_note_ids = session.query(NoteFundLink.note_id).filter(
            NoteFundLink.fund_id == fund_id
        ).all()
        fund_note_ids = [nid[0] for nid in fund_note_ids]

        lp_note_ids = session.query(NoteLPLink.note_id).filter(
            NoteLPLink.lp_id == lp_id
        ).all()
        lp_note_ids = [nid[0] for nid in lp_note_ids]

        # Find common note IDs
        common_note_ids = list(set(fund_note_ids) & set(lp_note_ids))

        if common_note_ids:
            # Get the latest note
            latest_note = session.query(Note).filter(
                Note.id.in_(common_note_ids)
            ).order_by(Note.date.desc()).first()

            if latest_note:
                record.last_contact_date = latest_note.date
                record.latest_note_id = latest_note.id

        session.commit()
        session.refresh(record)
        return record


# Roadshow endpoints
@app.get("/roadshows", response_model=List[Roadshow])
async def get_roadshows():
    """Get all roadshows"""
    with get_session() as session:
        roadshows = session.query(Roadshow).all()
        return roadshows


@app.post("/roadshows", response_model=Roadshow)
async def create_roadshow(roadshow_data: dict):
    """Create new roadshow"""
    from datetime import datetime

    with get_session() as session:
        # Convert date strings to datetime objects
        if 'arrival' in roadshow_data and roadshow_data['arrival']:
            if isinstance(roadshow_data['arrival'], str):
                roadshow_data['arrival'] = datetime.fromisoformat(roadshow_data['arrival'].replace('Z', '+00:00'))

        if 'second_arrival' in roadshow_data and roadshow_data['second_arrival']:
            if isinstance(roadshow_data['second_arrival'], str):
                roadshow_data['second_arrival'] = datetime.fromisoformat(roadshow_data['second_arrival'].replace('Z', '+00:00'))

        if 'departure' in roadshow_data and roadshow_data['departure']:
            if isinstance(roadshow_data['departure'], str):
                roadshow_data['departure'] = datetime.fromisoformat(roadshow_data['departure'].replace('Z', '+00:00'))

        # Create roadshow object
        roadshow = Roadshow(**roadshow_data)
        session.add(roadshow)
        session.commit()
        session.refresh(roadshow)

        # Update fund.roadshow_date if arrival is set
        if roadshow.arrival and roadshow.fund_id:
            fund = session.get(Fund, roadshow.fund_id)
            if fund:
                fund.roadshow_date = roadshow.arrival
                session.commit()

        return roadshow


@app.put("/roadshows/{roadshow_id}")
async def update_roadshow(roadshow_id: int, roadshow_update: dict):
    """Update roadshow"""
    from datetime import datetime

    with get_session() as session:
        roadshow = session.get(Roadshow, roadshow_id)
        if not roadshow:
            raise HTTPException(status_code=404, detail="Roadshow not found")

        # Convert date strings to datetime objects
        if 'arrival' in roadshow_update and roadshow_update['arrival']:
            if isinstance(roadshow_update['arrival'], str):
                roadshow_update['arrival'] = datetime.fromisoformat(roadshow_update['arrival'].replace('Z', '+00:00'))

        if 'second_arrival' in roadshow_update and roadshow_update['second_arrival']:
            if isinstance(roadshow_update['second_arrival'], str):
                roadshow_update['second_arrival'] = datetime.fromisoformat(roadshow_update['second_arrival'].replace('Z', '+00:00'))

        if 'departure' in roadshow_update and roadshow_update['departure']:
            if isinstance(roadshow_update['departure'], str):
                roadshow_update['departure'] = datetime.fromisoformat(roadshow_update['departure'].replace('Z', '+00:00'))

        # Update fields
        for key, value in roadshow_update.items():
            if key != 'id' and hasattr(roadshow, key):
                setattr(roadshow, key, value)

        session.commit()
        session.refresh(roadshow)

        # Update fund.roadshow_date if arrival changed
        if roadshow.arrival and roadshow.fund_id:
            fund = session.get(Fund, roadshow.fund_id)
            if fund:
                fund.roadshow_date = roadshow.arrival
                session.commit()

        return roadshow


@app.delete("/roadshows/{roadshow_id}")
async def delete_roadshow(roadshow_id: int):
    """Delete roadshow"""
    with get_session() as session:
        roadshow = session.get(Roadshow, roadshow_id)
        if not roadshow:
            raise HTTPException(status_code=404, detail="Roadshow not found")
        session.delete(roadshow)
        session.commit()
        return {"status": "deleted"}


# Roadshow LP Status endpoints (similar to Sales Funnel)
@app.get("/roadshows/{roadshow_id}/lp-status")
async def get_roadshow_lp_status(roadshow_id: int):
    """Get LP status funnel for a specific roadshow"""
    with get_session() as session:
        # Get the roadshow
        roadshow = session.get(Roadshow, roadshow_id)
        if not roadshow:
            raise HTTPException(status_code=404, detail="Roadshow not found")

        # Get all LPs
        lps = session.query(LP).all()

        result = []
        for lp in lps:
            # Check if there's a status record for this LP-Roadshow combo
            status_data = session.query(RoadshowLPStatus).filter(
                RoadshowLPStatus.roadshow_id == roadshow_id,
                RoadshowLPStatus.lp_id == lp.id
            ).first()

            # Find the most recent note related to BOTH this LP and this roadshow
            latest_note = (
                session.query(Note)
                .join(NoteLPLink, Note.id == NoteLPLink.note_id)
                .join(NoteRoadshowLink, Note.id == NoteRoadshowLink.note_id)
                .filter(NoteLPLink.lp_id == lp.id)
                .filter(NoteRoadshowLink.roadshow_id == roadshow_id)
                .order_by(Note.date.desc())
                .first()
            )

            # Extract note info
            last_contact_date = latest_note.date if latest_note else None
            latest_note_id = latest_note.id if latest_note else None

            # Determine status
            status = status_data.status if status_data else "inactive"

            item = {
                "roadshow_id": roadshow_id,
                "lp_id": lp.id,
                "lp_name": lp.name,
                "status": status,
                "last_contact_date": last_contact_date.isoformat() if last_contact_date else None,
                "latest_note_id": latest_note_id,
                # LP details
                "aum_billions": lp.aum_billions,
                "location": lp.location,
                "priority": lp.priority,
                "advisor": lp.advisor,
                "type_of_group": lp.type_of_group,
                "investment_low": lp.investment_low,
                "investment_high": lp.investment_high,
            }

            result.append(item)

        return result


@app.put("/roadshows/{roadshow_id}/lps/{lp_id}/status")
async def update_lp_roadshow_status(roadshow_id: int, lp_id: int, status: str):
    """Update LP status for a roadshow"""
    with get_session() as session:
        # Check if record exists
        record = session.query(RoadshowLPStatus).filter(
            RoadshowLPStatus.roadshow_id == roadshow_id,
            RoadshowLPStatus.lp_id == lp_id
        ).first()

        if record:
            # Update existing record
            record.status = status
        else:
            # Create new record
            record = RoadshowLPStatus(roadshow_id=roadshow_id, lp_id=lp_id, status=status)
            session.add(record)

        # Update last_contact_date by finding the latest note related to both roadshow and LP
        roadshow_note_ids = session.query(NoteRoadshowLink.note_id).filter(
            NoteRoadshowLink.roadshow_id == roadshow_id
        ).all()
        roadshow_note_ids = [nid[0] for nid in roadshow_note_ids]

        lp_note_ids = session.query(NoteLPLink.note_id).filter(
            NoteLPLink.lp_id == lp_id
        ).all()
        lp_note_ids = [nid[0] for nid in lp_note_ids]

        # Find common note IDs
        common_note_ids = list(set(roadshow_note_ids) & set(lp_note_ids))

        if common_note_ids:
            # Get the latest note
            latest_note = session.query(Note).filter(
                Note.id.in_(common_note_ids)
            ).order_by(Note.date.desc()).first()

            if latest_note:
                record.last_contact_date = latest_note.date
                record.latest_note_id = latest_note.id

        session.commit()
        session.refresh(record)
        return record


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
