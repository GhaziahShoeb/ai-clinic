from sqlalchemy import Column, Integer, String, Enum
from database import Base
import enum

# Define the 3 roles as a strict enum — only these 3 values allowed
class UserRole(enum.Enum):
    patient = "patient"
    doctor  = "doctor"
    admin   = "admin"

# This class = one table in PostgreSQL called "users"
class User(Base):
    __tablename__ = "users"

    id       = Column(Integer, primary_key=True, index=True)  # auto ID for each user
    name     = Column(String, nullable=False)                  # full name
    email    = Column(String, unique=True, index=True)         # login email, must be unique
    password = Column(String, nullable=False)                  # hashed password (never plain text)
    role     = Column(Enum(UserRole), nullable=False)          # patient / doctor / admin