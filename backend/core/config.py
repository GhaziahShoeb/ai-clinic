from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SECRET_KEY:   str = os.getenv("SECRET_KEY")
    ALGORITHM:    str = os.getenv("ALGORITHM")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")

# single instance used across the whole app
# import this wherever you need a setting
settings = Settings()