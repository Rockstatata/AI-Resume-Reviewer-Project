from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class JobMatch(SQLModel, table=True):
    __tablename__ = "job_matches"
    id: int = Field(default=None, primary_key=True)
    resume_id: int = Field(foreign_key="resumes.id")
    user_id: int = Field(foreign_key="users.id")
    job_description: str
    ai_response: str  # Store as JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
