class RiskService:
    def assess_risk(self, data, prediction, confidence):
        score = 0
        score += 30 if data.get('glucose',0)>=140 else 20 if data.get('glucose',0)>=126 else 10 if data.get('glucose',0)>=100 else 0
        score += 20 if data.get('bmi',0)>=35 else 15 if data.get('bmi',0)>=30 else 8 if data.get('bmi',0)>=25 else 0
        score += 15 if data.get('blood_pressure',0)>=100 else 10 if data.get('blood_pressure',0)>=90 else 0
        score += 10 if data.get('age',0)>=55 else 6 if data.get('age',0)>=45 else 0
        score += confidence*10 if prediction else 0
        level = 'High' if score >= 60 or (prediction and confidence >= .8) else 'Medium' if score >= 35 or prediction else 'Low'
        return {'risk_level':level,'risk_score':round(min(score,100),2),'risk_factors':{},'recommendation_priority':'Urgent' if level=='High' else 'Routine'}
