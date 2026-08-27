from pathlib import Path
from backend.config import settings
class ReportService:
    def generate_report(self, patient, prediction, insights, risk):
        path = settings.resolved_reports_dir / f"report_{prediction.get('patient_id','unknown')}.txt"
        path.write_text(f"MEDIMIND REPORT\nPatient: {patient.get('name')}\nPrediction: {prediction.get('prediction_label')}\nRisk: {risk.get('risk_level')}\n{insights.get('explanation','')}", encoding='utf-8')
        return str(path)
