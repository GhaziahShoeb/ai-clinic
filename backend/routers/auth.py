from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.user import UserCreate, UserOut
from services.auth_service import create_user, get_user_by_email, login_user
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])

# input shape for login
class LoginRequest(BaseModel):
    email:    str
    password: str

# POST /auth/register — creates a new user
@router.post("/register", response_model=UserOut)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db, user_data)

# POST /auth/login — returns JWT token
@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    result = login_user(db, data.email, data.password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return result