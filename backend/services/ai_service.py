from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base

# import all models so SQLAlchemy knows about them when creating tables
from models import user, patient, appointment

app = FastAPI(title="AI Clinic API")

# CORS — allows React (localhost:5173) to talk to FastAPI (localhost:8000)
# without this the browser blocks all requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# creates all tables in Neon on startup if they don't exist
@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)

# test route — just to confirm server is running
@app.get("/")
def root():
    return {"message": "AI Clinic API is running"}