from pydantic import BaseModel
from typing import Optional
class PatientCreate(BaseModel):
    age: int
    blood_type: str
    allergies: Optional[str] = None
    medicatios: Optional[str] = None
    notes: Optional[str] = None

class PatientOut(BaseModel):
    id: int
    age: int
    blood_type: str
    allergies: Optional[str] = None
    conditions: Optional[str] = None
    medicatios: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True

