"""
Database models and ORM logic for CRM application
Uses SQLModel (Pydantic + SQLAlchemy) for type-safe database operations
"""

from sqlmodel import SQLModel, Field, Relationship, create_engine, Session
from typing import Optional, List
from datetime import datetime
import os


# Database models
class Distributor(SQLModel, table=True):
    """Distributor organizations"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    # Relationships
    gps: List["GP"] = Relationship(back_populates="distributor")


class LP(SQLModel, table=True):
    """Limited Partner organization"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    # LP Details from Notion
    aum_billions: Optional[float] = None  # AUM in billions
    advisor: Optional[str] = None  # Advisor information
    intl_alts: Optional[str] = None  # International Alternatives interest
    intl_mf: Optional[str] = None  # International Multi-Family interest
    local_alts: Optional[str] = None  # Local Alternatives interest
    local_mf: Optional[str] = None  # Local Multi-Family interest
    investment_high: Optional[float] = None  # High investment amount
    investment_low: Optional[float] = None  # Low investment amount
    location: Optional[str] = None  # Location
    priority: Optional[str] = None  # Priority level
    type_of_group: Optional[str] = None  # Type of LP group
    text: Optional[str] = None  # General notes/text

    # Relationships
    notes: List["Note"] = Relationship(back_populates="lp")


# Many-to-many relationship tables
class GPLPLink(SQLModel, table=True):
    """Link table for GP-LP many-to-many relationship"""
    gp_id: int = Field(foreign_key="gp.id", primary_key=True)
    lp_id: int = Field(foreign_key="lp.id", primary_key=True)


class GPPersonLink(SQLModel, table=True):
    """Link table for GP-Person many-to-many relationship"""
    gp_id: int = Field(foreign_key="gp.id", primary_key=True)
    person_id: int = Field(foreign_key="person.id", primary_key=True)


class LPPersonLink(SQLModel, table=True):
    """Link table for LP-Person many-to-many relationship"""
    lp_id: int = Field(foreign_key="lp.id", primary_key=True)
    person_id: int = Field(foreign_key="person.id", primary_key=True)


class GP(SQLModel, table=True):
    """General Partner organization"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    location: Optional[str] = None
    contact_level: Optional[str] = None  # e.g., "Partner", "Open Dialogue", etc.
    flagship_strategy: Optional[str] = None
    other_strategies: Optional[str] = None
    note: Optional[str] = None  # General notes about the GP

    # Foreign keys
    distributor_id: Optional[int] = Field(default=None, foreign_key="distributor.id")

    # Relationships
    distributor: Optional[Distributor] = Relationship(back_populates="gps")
    notes: List["Note"] = Relationship(back_populates="gp")  # Related Notes
    # Many-to-many relationships handled via link tables


class Person(SQLModel, table=True):
    """Individual contact person"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    # Contact details
    cell_phone: Optional[str] = None
    office_phone: Optional[str] = None
    email: Optional[str] = None
    location: Optional[str] = None

    # Professional details
    position: Optional[str] = None  # Job title/position
    people_type: Optional[str] = None  # LP, GP, Distributor, Other (can be multiple)
    personal_note: Optional[str] = None  # Personal notes about the person

    # Legacy fields (keeping for backwards compatibility)
    role: Optional[str] = None  # Deprecated - use position instead
    org_type: Optional[str] = None  # Deprecated - use people_type instead
    org_id: Optional[int] = None  # Deprecated


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
