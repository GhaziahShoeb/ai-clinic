from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

class Patient(Base):
    __tablename__ = "patients"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), unique=True)  # links to users table
    age        = Column(Integer, nullable=False)
    blood_type = Column(String, nullable=False)                        # e.g. A+, O-
    allergies  = Column(Text, nullable=True)                           # comma separated
    conditions = Column(Text, nullable=True)                           # e.g. diabetes, hypertension
    medications= Column(Text, nullable=True)                           # current meds
    notes      = Column(Text, nullable=True)                           # doctor's clinical notes

    # tells SQLAlchemy: patient belongs to a user
    user = relationship("User", backref="patient")