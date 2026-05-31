from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Appointment(Base):
    __tablename__ = "appointments"  # table name in PostgreSQL

    id = Column(Integer, primary_key=True, index=True)  # unique ID per appointment

    patient_id = Column(Integer, ForeignKey("patients.id"))  
    # which patient is this appointment for?
    # must exist in patients table — can't book for a ghost patient

    doctor_id = Column(Integer, ForeignKey("users.id"))  
    # which doctor is seeing them?
    # doctors are users too, so we point to users table

    date = Column(DateTime)       # actual date + time of appointment
    status = Column(String, default="scheduled")  
    # default = "scheduled" means if you don't pass a status, it auto-sets this

    reason = Column(String)       # why did the patient come in

    # these two lines let you write:
    # appointment.patient.name  instead of a SQL join
    # appointment.doctor.name   instead of a SQL join
    patient = relationship("Patient", backref="appointments")
    doctor  = relationship("User", backref="appointments")