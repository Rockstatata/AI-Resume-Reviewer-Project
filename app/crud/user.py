from sqlmodel import Session, select
from app.models.user import User

def get_user_by_email(session: Session, email: str):
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()