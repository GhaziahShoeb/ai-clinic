from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User, UserRole
from models.patient import Patient
from models.appointment import Appointment
from schemas.patient import PatientOut
from core.security import get_current_user

router = APIRouter(prefix="/doctors", tags=["doctors"])

# only allow doctors
def require_doctor(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.doctor:
        raise HTTPException(status_code=403, detail="Doctors only")
    return current_user

# GET /doctors/patients — doctor sees all patients
@router.get("/patients", response_model=list[PatientOut])
def get_my_patients(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor)
):
    return db.query(Patient).all()

# GET /doctors/appointments — doctor sees their appointments
@router.get("/appointments")
def get_my_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor)
):
    appointments = db.query(Appointment).filter(
        Appointment.doctor_id == current_user.id
    ).all()
    return appointments