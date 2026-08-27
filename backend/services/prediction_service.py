from pathlib import Path
from typing import Optional
import joblib
from backend.config import settings
from backend.utils.clean_data import extract_feature_vector
_model = None

class PredictionService:
    def __init__(self, model_path: Optional[Path] = None): self.model_path = model_path or settings.resolved_model_path
    def load_model(self):
        global _model
        if _model is not None: return True
        if not self.model_path.exists(): return False
        _model = joblib.load(self.model_path); return True
    def select_model(self, data): return 'diabetes_random_forest'
    def predict(self, data):
        if not self.load_model(): return self.fallback(data)
        try:
            vector = extract_feature_vector(data)
            probabilities = _model.predict_proba([vector])[0]
            prediction = int(_model.predict([vector])[0])
            confidence = float(max(probabilities))
            return {'disease':'Diabetes','model':type(_model).__name__,'prediction':prediction,'prediction_label':'Positive' if prediction else 'Negative','confidence':round(confidence,4),'probabilities':{'negative':float(probabilities[0]),'positive':float(probabilities[1])},'feature_vector':vector}
        except Exception: return self.fallback(data)
    def fallback(self, data):
        risk = sum([data.get('age',30)>50, data.get('bmi',25)>=30, data.get('glucose',100)>=140])
        prediction = int(risk >= 2); confidence = min(.5 + risk*.15, .9)
        return {'disease':'Diabetes','model':'Rule-Based Fallback','prediction':prediction,'prediction_label':'Positive' if prediction else 'Negative','confidence':confidence,'probabilities':{'negative':1-confidence if prediction else confidence,'positive':confidence if prediction else 1-confidence},'feature_vector':[]}
