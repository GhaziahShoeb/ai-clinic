from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User, UserRole
from models.patient import Patient
from schemas.patient import PatientCreate, PatientOut
from core.security import get_current_user
from models.user import User, UserRole
from models.patient import Patient
from sqlalchemy.orm import Session

router = APIRouter(prefix="/patients", tags=["patients"])

# only allow doctors and admins
def require_doctor_or_admin(current_user: User = Depends(get_current_user)):
    if current_user.role not in [UserRole.doctor, UserRole.admin]:
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user

# POST /patients — admin creates a patient record
@router.post("/", response_model=PatientOut)
def create_patient(
    data: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Only admins can create patients")
    patient = Patient(**data.dict())  # user_id comes from data now
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient

# GET /patients — doctor/admin gets all patients
@router.get("/", response_model=list[PatientOut])
def get_all_patients(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin)
):
    return db.query(Patient).all()

# GET /patients/me — patient sees their own record
@router.get("/me", response_model=PatientOut)
def get_my_record(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient record not found")
    return patient

# GET /patients/{id} — doctor/admin gets a specific patient
@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor_or_admin)
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient
