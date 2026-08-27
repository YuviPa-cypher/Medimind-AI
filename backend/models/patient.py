from typing import Optional
from pydantic import BaseModel, Field

class PatientCreate(BaseModel):
    name: str = Field(..., min_length=1)
    age: int = Field(..., ge=1, le=120)
    gender: str
    glucose: float = Field(..., ge=0, le=500)
    blood_pressure: float = Field(..., ge=0, le=200)
    bmi: float = Field(..., ge=10, le=70)
    diabetes_pedigree: float = Field(..., ge=0, le=3)
    insulin: float = Field(0, ge=0, le=900)
    skin_thickness: float = Field(0, ge=0, le=100)
    pregnancies: int = Field(0, ge=0, le=20)

class PatientResponse(PatientCreate):
    id: str
    doctor_id: Optional[str] = None
