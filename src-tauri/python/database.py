"""
Database models and ORM logic for CRM application
Uses SQLModel (Pydantic + SQLAlchemy) for type-safe database operations
"""

from sqlmodel import SQLModel, Field, Relationship, create_engine, Session
from typing import Optional, List
from datetime import datetime
import os


# Database models
class LP(SQLModel, table=True):
    """Limited Partner organization"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    # Relationships
    notes: List["Note"] = Relationship(back_populates="lp")


class GP(SQLModel, table=True):
    """General Partner organization"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    # Relationships
    notes: List["Note"] = Relationship(back_populates="gp")


class Person(SQLModel, table=True):
    """Individual contact person"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    role: str
    org_type: str  # LP/GP/Other
    org_id: Optional[int] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class Note(SQLModel, table=True):
    """Meeting notes and summaries"""
    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime = Field(default_factory=datetime.now)

    # Foreign keys
    lp_id: Optional[int] = Field(default=None, foreign_key="lp.id")
    gp_id: Optional[int] = Field(default=None, foreign_key="gp.id")

    # Relationships
    lp: Optional[LP] = Relationship(back_populates="notes")
    gp: Optional[GP] = Relationship(back_populates="notes")

    # Note content
    raw_notes: str = ""
    summary: str = ""
    fundraise: Optional[str] = None
    interest: Optional[str] = None  # Sales funnel stage

    # Audio metadata
    audio_path: Optional[str] = None
    transcription_path: Optional[str] = None

    # Todos
    todos: List["Todo"] = Relationship(back_populates="note")


class Todo(SQLModel, table=True):
    """Action items from meetings"""
    id: Optional[int] = Field(default=None, primary_key=True)
    note_id: int = Field(foreign_key="note.id")
    description: str
    status: str = "pending"  # pending/completed
    due_date: Optional[datetime] = None

    # Relationship
    note: Optional[Note] = Relationship(back_populates="todos")


# Database setup
DB_PATH = os.path.join(os.path.dirname(__file__), "../../db/crm.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    """Initialize database and create all tables"""
    # Ensure db directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get database session for operations"""
    return Session(engine)


if __name__ == "__main__":
    # Create tables when running directly
    create_db_and_tables()
    print(f"Database initialized at: {DB_PATH}")
