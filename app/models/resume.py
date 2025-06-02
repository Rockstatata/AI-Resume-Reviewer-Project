from sqlmodel import SQLModel, Field
from typing import Optional

class Resume(SQLModel, table=True):
    __tablename__ = "resumes"
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    filename: str
    content: str  
    uploaded_at: Optional[str]