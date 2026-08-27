import httpx
from backend.config import settings
from backend.utils.logger import logger

class GeminiService:
    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.models = ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-2.5-flash-lite"]

    async def chat(self, message: str, **kwargs) -> str:
        if not message or not message.strip():
            return "Please provide a valid medical query or question."

        if not self.api_key:
            return self._fallback_chat_reply(message)

        prompt = (
            "You are MEDIMIND AI, an advanced medical decision-support assistant and clinical decision copilot. "
            "Provide helpful, accurate, well-formatted medical advice and information in clear natural language. "
            "Include general health considerations, over-the-counter options when applicable, and advice on when to consult a medical professional.\n\n"
            f"User query: {message.strip()}"
        )

        async with httpx.AsyncClient(timeout=25.0) as client:
            for model_name in self.models:
                try:
                    url = f"{self.base_url}/{model_name}:generateContent?key={self.api_key}"
                    payload = {"contents": [{"parts": [{"text": prompt}]}]}
                    response = await client.post(url, json=payload)
                    if response.status_code == 200:
                        data = response.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts and "text" in parts[0]:
                                return parts[0]["text"].strip()
                except Exception as err:
                    logger.warning(f"Gemini API model {model_name} error: {err}")

        return self._fallback_chat_reply(message)

    def _fallback_chat_reply(self, message: str) -> str:
        msg = message.lower()
        if "gas" in msg or "bloat" in msg or "indigestion" in msg:
            return (
                "For gas and bloating, common over-the-counter medicines include:\n"
                "• Simethicone (e.g., Gas-X, Phazyme) - Breaks up gas bubbles in the gut for easier passage.\n"
                "• Alpha-galactosidase (e.g., Beano) - Enzyme supplement taken before meals to help digest gas-producing foods.\n"
                "• Activated Charcoal - Absorbs excess gas in the digestive tract.\n"
                "• Antacids / H2 Blockers (e.g., Famotidine, Omeprazole) - If gas is accompanied by heartburn or acid reflux.\n\n"
                "Lifestyle Tip: Eat slowly, limit carbonated beverages, and stay active. "
                "If symptoms are accompanied by severe abdominal pain, persistent vomiting, or black stools, seek medical evaluation."
            )
        return (
            "MEDIMIND AI Assistant: I am ready to assist with your clinical questions. "
            "Please ask about symptoms, medications, diagnostic guidelines, or health management."
        )

    async def generate_clinical_insights(self, data, prediction, risk):
        label = prediction.get('prediction_label', 'Evaluated')
        conf = prediction.get('confidence', 0.8)
        
        prompt = (
            f"As MEDIMIND AI medical expert, generate concise clinical insights for a patient evaluation:\n"
            f"Metrics: Age {data.get('age')}, Glucose {data.get('glucose')} mg/dL, BP {data.get('blood_pressure')} mmHg, BMI {data.get('bmi')}.\n"
            f"Model Prediction: {label} (Confidence: {conf:.1%}), Risk Level: {risk.get('risk_level')}.\n"
            f"Provide a brief 2-sentence clinical explanation, recommended follow-up tests, and lifestyle recommendations."
        )
        
        explanation = f"The screening result indicates {label} with {conf:.1%} confidence. Key risk indicators include glucose ({data.get('glucose')} mg/dL) and BMI ({data.get('bmi')})."
        recommended_tests = ['HbA1c Test', 'Fasting Plasma Glucose', 'Lipid Panel', 'Renal Function Test']
        
        if self.api_key:
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    url = f"{self.base_url}/gemini-3.6-flash:generateContent?key={self.api_key}"
                    payload = {"contents": [{"parts": [{"text": prompt}]}]}
                    r = await client.post(url, json=payload)
                    if r.status_code == 200:
                        txt = r.json()['candidates'][0]['content']['parts'][0]['text'].strip()
                        explanation = txt
            except Exception as e:
                logger.warning(f"Clinical insights API call fallback: {e}")
                
        return {
            'explanation': explanation,
            'recommended_tests': recommended_tests,
            'lifestyle_changes': ['Balanced low-glycemic diet', '30 minutes daily moderate exercise', 'Regular glycemic monitoring'],
            'medication_disclaimer': 'Consult a licensed healthcare professional before changing medication.',
            'doctor_notes': 'Clinical follow-up recommended.',
            'source': 'gemini-3.6-flash'
        }
