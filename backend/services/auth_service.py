from sqlalchemy.orm import Session
from models.user import User, UserRole
from schemas.user import UserCreate
from core.security import hash_password, verify_password, create_access_token

# creates a new user in the database
def create_user(db: Session, user_data: UserCreate):
    hashed = hash_password(user_data.password)  # never store plain password
    new_user = User(
        name     = user_data.name,
        email    = user_data.email,
        password = hashed,
        role     = user_data.role
    )
    db.add(new_user)      # stage the new user
    db.commit()           # save to Neon
    db.refresh(new_user)  # get the auto-generated id back
    return new_user

# finds a user by email
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# verifies login and returns a JWT token
def login_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    token = create_access_token({"sub": user.email, "role": user.role.value})
    return {"access_token": token, "token_type": "bearer"}