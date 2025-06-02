from pydantic import BaseModel

class ResumeUpload(BaseModel):
    filename: str

class ResumeRead(BaseModel):
    id: int
    filename: str
    content: str
    uploaded_at: str