from pydantic import BaseModel, EmailStr
from enum import Enum

# same roles as the model
class UserRole(str, Enum):
    patient = "patient"
    doctor  = "doctor"
    admin   = "admin"

# what we need to CREATE a user (input)
class UserCreate(BaseModel):
    name:     str
    email:    EmailStr  # validates it's a real email format
    password: str
    role:     UserRole

# what we send BACK to frontend (output) — no password!
class UserOut(BaseModel):
    id:    int
    name:  str
    email: str
    role:  UserRole

    class Config:
        from_attributes = True  # lets pydantic read SQLAlchemy objects