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
    notion_id: Optional[str] = Field(default=None, index=True, unique=True)  # Notion page ID
    name: str = Field(index=True)

    # Distributor details
    headquarter: Optional[str] = None  # Headquarters location
    mexico: Optional[str] = None  # Mexico presence/info
    text: Optional[str] = None  # General notes

    # Relationships
    gps: List["GP"] = Relationship(back_populates="distributor")  # One-to-many via GP.distributor_id
    # Many-to-many with Person handled via DistributorPersonLink


class LP(SQLModel, table=True):
    """Limited Partner organization"""
    id: Optional[int] = Field(default=None, primary_key=True)
    notion_id: Optional[str] = Field(default=None, index=True, unique=True)  # Notion page ID
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

    # Relationships via link tables
    # Many-to-many with Note handled via NoteLPLink
    # Many-to-many with Person handled via LPPersonLink


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


class DistributorPersonLink(SQLModel, table=True):
    """Link table for Distributor-Person many-to-many relationship"""
    distributor_id: int = Field(foreign_key="distributor.id", primary_key=True)
    person_id: int = Field(foreign_key="person.id", primary_key=True)


class NoteGPLink(SQLModel, table=True):
    """Link table for Note-GP many-to-many relationship"""
    note_id: int = Field(foreign_key="note.id", primary_key=True)
    gp_id: int = Field(foreign_key="gp.id", primary_key=True)


class NoteLPLink(SQLModel, table=True):
    """Link table for Note-LP many-to-many relationship"""
    note_id: int = Field(foreign_key="note.id", primary_key=True)
    lp_id: int = Field(foreign_key="lp.id", primary_key=True)


class NoteDistributorLink(SQLModel, table=True):
    """Link table for Note-Distributor many-to-many relationship"""
    note_id: int = Field(foreign_key="note.id", primary_key=True)
    distributor_id: int = Field(foreign_key="distributor.id", primary_key=True)


class NoteFundLink(SQLModel, table=True):
    """Link table for Note-Fund many-to-many relationship"""
    note_id: int = Field(foreign_key="note.id", primary_key=True)
    fund_id: int = Field(foreign_key="fund.id", primary_key=True)


class FundLPInterest(SQLModel, table=True):
    """Track LP interest level for each Fund (Sales Funnel)"""
    fund_id: int = Field(foreign_key="fund.id", primary_key=True)
    lp_id: int = Field(foreign_key="lp.id", primary_key=True)

    # Sales funnel interest levels
    interest: str = "inactive"  # inactive, commitment, due_diligence, interested, meeting, meeting_offered, no_reply, low_probability

    # Auto-updated fields
    last_contact_date: Optional[datetime] = None  # Date of last note related to both fund and LP
    latest_note_id: Optional[int] = None  # ID of the latest related note


class GP(SQLModel, table=True):
    """General Partner organization"""
    id: Optional[int] = Field(default=None, primary_key=True)
    notion_id: Optional[str] = Field(default=None, index=True, unique=True)  # Notion page ID
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
    # Many-to-many with Note handled via NoteGPLink
    # Many-to-many with LP handled via GPLPLink
    # Many-to-many with Person handled via GPPersonLink


class Person(SQLModel, table=True):
    """Individual contact person"""
    id: Optional[int] = Field(default=None, primary_key=True)
    notion_id: Optional[str] = Field(default=None, index=True, unique=True)  # Notion page ID
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
    """Meeting notes and summaries from Notion"""
    id: Optional[int] = Field(default=None, primary_key=True)
    notion_id: Optional[str] = Field(default=None, index=True, unique=True)  # Notion page ID for matching

    name: str  # Note title
    date: Optional[datetime] = None

    # Notion properties
    contact_type: Optional[str] = None
    local_mf: Optional[str] = None  # Local Multi-Family
    local_alts: Optional[str] = None  # Local Alternatives
    intl_mf: Optional[str] = None  # International Multi-Family
    intl_alts: Optional[str] = None  # International Alternatives
    roadshows: Optional[str] = None
    pin: Optional[str] = None
    useful: Optional[bool] = None  # Checkbox field
    fundraise: Optional[str] = None
    ai_summary: Optional[str] = None

    # Note content (from blocks)
    content_text: Optional[str] = None  # Plain text extracted from all blocks
    content_json: Optional[str] = None  # Full block structure as JSON

    # Image references
    image_paths: Optional[str] = None  # Comma-separated local image paths

    # Legacy fields (for compatibility with existing code)
    raw_notes: Optional[str] = ""
    summary: Optional[str] = ""
    interest: Optional[str] = None  # Sales funnel stage
    audio_path: Optional[str] = None
    transcription_path: Optional[str] = None

    # Relationships via link tables (many-to-many)
    # GPs, LPs, Distributors handled via NoteGPLink, NoteLPLink, NoteDistributorLink

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


class Fund(SQLModel, table=True):
    """Investment funds from Notion"""
    id: Optional[int] = Field(default=None, primary_key=True)
    notion_id: Optional[str] = Field(default=None, index=True, unique=True)  # Notion page ID

    # Core fields
    fund_name: str = Field(index=True)

    # Fund details from Notion
    geography: Optional[str] = None
    target_multiple: Optional[float] = None
    status: Optional[str] = None
    days_to_rs: Optional[int] = None
    target_irr: Optional[str] = None  # Can be "20+" etc
    hard_cap_mn: Optional[float] = None  # Hard cap in millions
    target_mn: Optional[float] = None  # Target in millions
    roadshow_date: Optional[datetime] = None
    sectors: Optional[str] = None  # Comma-separated
    note: Optional[str] = None  # General notes
    potential: Optional[str] = None
    asset_class: Optional[str] = None
    current_lps: Optional[str] = None  # Current LPs info
    launch: Optional[datetime] = None
    roadshows: Optional[str] = None
    final_close: Optional[datetime] = None
    closed: Optional[bool] = None

    # GP relationship - stored as notion_id reference
    gp_notion_id: Optional[str] = None  # Reference to GP's notion_id

    # Many-to-many with Note handled via NoteFundLink


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
