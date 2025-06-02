from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Review(SQLModel, table=True):
    __tablename__ = "reviews"
    id: int = Field(default=None, primary_key=True)
    resume_id: int = Field(foreign_key="resumes.id")
    user_id: int = Field(foreign_key="users.id")
    feedback: str
    score: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)