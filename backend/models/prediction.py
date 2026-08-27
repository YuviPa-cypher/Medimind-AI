from typing import Optional, List
from pydantic import BaseModel, Field

class PredictionRequest(BaseModel):
    patient_id: Optional[str] = None
    name: str
    age: int
    gender: str
    glucose: float
    blood_pressure: float
    bmi: float
    diabetes_pedigree: float
    insulin: float = 0
    skin_thickness: float = 0
    pregnancies: int = 0

class PredictionResponse(BaseModel):
    patient_id: str
    prediction_id: str
    disease: str
    prediction: int
    prediction_label: str
    confidence: float
    risk_level: str
    risk_score: float
    explanation: str = ''
    recommended_tests: List[str] = []
    lifestyle_changes: List[str] = []
    report_path: Optional[str] = None
