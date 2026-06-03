from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load variables from your .env file into the environment
load_dotenv()

# Read the database URL from .env (your Neon connection string)
DATABASE_URL = os.getenv("DATABASE_URL")

# Create the connection to the database
# This is the actual "door" to your PostgreSQL on Neon
engine = create_engine(DATABASE_URL)

# SessionLocal is a factory that creates database sessions
# Each session = one conversation with the database (read/write)
# autocommit=False → we manually control when to save changes
# autoflush=False  → don't auto-send changes before every query
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class all your models will inherit from
# e.g. class User(Base) → SQLAlchemy knows User is a DB table
Base = declarative_base()

# This is a dependency FastAPI will inject into every route
# It opens a DB session, gives it to the route, then closes it
# "yield" means: give the session to whoever asked, then come back to close it
def get_db():
    db = SessionLocal()
    try:
        yield db        # route uses the session here
    finally:
        db.close()      # always close, even if an error happened¸