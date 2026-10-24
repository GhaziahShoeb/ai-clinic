from fastapi import APIRouter, Depends, HTTPException, Body, Request

from sqlalchemy.orm import Session
from database import get_db
from schemas.user import UserCreate, UserOut
from services.auth_service import create_user, get_user_by_email, login_user
from pydantic import BaseModel
from core.security import get_current_user
from models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email:    str
    password: str

# POST /auth/register
@router.post("/register", response_model=UserOut)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db, user_data)

# POST /auth/login — supports OAuth2 form (unchanged)
@router.post("/login")
async def login(
    request: Request,
    db: Session = Depends(get_db)
):
    """Accepts either JSON payload or form‑encoded body.

    * JSON: {"email": "...", "password": "..."}
    * Form‑encoded (OAuth2 style): username=...&password=...
    """
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        body = await request.json()
        email = body.get("email")
        pwd = body.get("password")
    elif "application/x-www-form-urlencoded" in content_type:
        form = await request.form()
        email = form.get("username")
        pwd = form.get("password")
    else:
        raise HTTPException(
            status_code=415,
            detail="Unsupported Content-Type. Use JSON or form data."
        )
    if not email or not pwd:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    result = login_user(db, email, pwd)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return result


@router.get("/me",response_model=UserOut)
def get_me(current_user: User =Depends(get_current_user)):
    return current_user