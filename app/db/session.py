from fastapi import Depends
from sqlmodel import SQLModel, create_engine, Session
import os
from dotenv import load_dotenv
from typing import Annotated

load_dotenv()
DATABASE_URL = os.getenv("SQL_MODEL_DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session
        
SessionDep = Annotated[Session, Depends(get_session)]