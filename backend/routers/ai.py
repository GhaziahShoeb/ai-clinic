from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User, UserRole
from models.patient import Patient
from core.security import get_current_user
from services.ai_service import ask_about_patient
from services.embedding_service import embed_patient
from pydantic import BaseModel

router = APIRouter(prefix="/ai", tags=["ai"])

class QuestionRequest(BaseModel):
    question: str

# POST /ai/embed/{patient_id} — embed a patient's record into ChromaDB
@router.post("/embed/{patient_id}")
def embed_patient_record(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.doctor, UserRole.admin]:
        raise HTTPException(status_code=403, detail="Not authorized")

    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # build clinical text from patient record
    text = f"""
    Patient ID: {patient.id}
    Age: {patient.age}
    Blood Type: {patient.blood_type}
    Allergies: {patient.allergies or 'None'}
    Conditions: {patient.conditions or 'None'}
    Medications: {patient.medications or 'None'}
    Clinical Notes: {patient.notes or 'None'}
    """

    embed_patient(patient.id, text)
    return {"message": f"Patient {patient_id} record embedded successfully"}

# POST /ai/ask/{patient_id} — doctor asks a question about a patient
@router.post("/ask/{patient_id}")
def ask_question(
    patient_id: int,
    request: QuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.doctor, UserRole.admin]:
        raise HTTPException(status_code=403, detail="Not authorized")

    answer = ask_about_patient(patient_id, request.question)
    return {"answer": answer}

from services.ai_service import ask_about_patient, generate_patient_summary

# GET /ai/summary/{patient_id} — generate patient summary
@router.get("/summary/{patient_id}")
def get_patient_summary(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in [UserRole.doctor, UserRole.admin]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    summary = generate_patient_summary(patient_id)
    return {"summary": summary}