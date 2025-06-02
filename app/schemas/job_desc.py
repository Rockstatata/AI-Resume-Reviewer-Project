from pydantic import BaseModel
from typing import Any
from datetime import datetime

class JobMatchRead(BaseModel):
    id: int
    resume_id: int
    user_id: int
    job_description: str
    ai_response: Any
    created_at: datetime