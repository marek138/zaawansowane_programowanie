from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from users_db import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    roles: Mapped[str] = mapped_column(String)
