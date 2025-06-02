from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: int = Field(default=None, primary_key=True)
    email: str
    hashed_password: str
    is_active: bool = True
    role: str = Field(default="user")