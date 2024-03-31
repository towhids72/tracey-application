from sqlalchemy import Boolean, String

from sqlalchemy import Column, Integer
from sqlalchemy.orm import DeclarativeBase


class BaseSQL(DeclarativeBase):
    __abstract__ = True

    id = Column(Integer, primary_key=True)


class UserModel(BaseSQL):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)
