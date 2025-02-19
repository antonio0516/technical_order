from sqlalchemy import Boolean, Column, Index, Integer, String

from domain.database.database import Base


class User(Base):
    __tablename__ = "user"

    account = Column(String(100), primary_key=True, index=True)
    hashed_password = Column(String(64), nullable=False)
    salt = Column(String(32), nullable=False)
    is_admin = Column(Boolean, nullable=False, default=True)
