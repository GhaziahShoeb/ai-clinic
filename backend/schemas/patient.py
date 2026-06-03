from pydantic import BaseModel
from typing import Optional
class PatientCreate(BaseModel):
    user_id:    int
    age:        int
    blood_type: str
    allergies:  Optional[str] = None
    conditions: Optional[str] = None
    medications:Optional[str] = None
    notes:      Optional[str] = None

class PatientOut(BaseModel):
    id: int
    age: int
    name: Optional[str] = None 
    blood_type: str
    allergies: Optional[str] = None
    conditions: Optional[str] = None
    medications: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True

