import os
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.tokens import Token
from app.crud.user import get_user_by_email
from app.auth.jwt import create_access_token
from app.db.session import SessionDep
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.utils.file_utils import hash_password, verify_password
from fastapi import Request
from typing import Set

router = APIRouter()

@router.post("/login", response_model=Token)
def login(user: UserCreate, session: SessionDep):
    db_user = get_user_by_email(session, user.email)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=403, detail="Invalid credentials")
    token = create_access_token({"sub": db_user.email, "id": db_user.id})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, session: SessionDep):
    db_user = get_user_by_email(session, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = hash_password(user.password)  
    admin_email = os.getenv("ADMIN_EMAIL")
    role = "admin" if user.email == admin_email else "user"
    new_user = User(email=user.email, hashed_password=hashed_pw, is_active=True, role=role)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout():
    return {"message": "Logout successful. Please delete your token on the client."}