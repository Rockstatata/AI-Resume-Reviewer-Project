from fastapi import FastAPI
from app.db.base import create_db_and_tables
from contextlib import asynccontextmanager

from app.api import auth, resume, admin, job_match

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router, prefix="/auth" , tags=["auth"])
app.include_router(resume.router, prefix="/resume" , tags=["resume"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(job_match.router, prefix="/job_match", tags=["job-match"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Resume Reviewer API"}
