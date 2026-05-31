from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AppointmentCreate(BaseModel):
    doctor_id: int
    patient_id: int
    appointment_time: datetime
    reason: Optional[str] = None

class AppointmentOut(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    appointment_time: datetime
    reason: Optional[str] = None

    class Config:
        from_attributes = True