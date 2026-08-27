import os
from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / '.env')

class Settings(BaseSettings):
    app_name: str = 'MEDIMIND'
    debug: bool = True
    secret_key: str = 'change-this-secret'
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 60
    mongodb_uri: str = 'mongodb://localhost:27017'
    mongodb_db: str = 'medimind'
    gemini_api_key: str = ''
    reports_dir: str = 'reports'
    model_path: str = 'backend/trained_models/disease_model.pkl'
    default_doctor_email: str = 'doctor@medimind.com'
    default_doctor_password: str = 'doctor123'
    default_doctor_name: str = 'Dr. Admin'
    frontend_url: str = 'http://localhost:5173'

    class Config:
        env_file = '.env'
        extra = 'ignore'

    @property
    def resolved_model_path(self):
        path = Path(self.model_path)
        return path if path.is_absolute() else ROOT_DIR / path

    @property
    def resolved_reports_dir(self):
        path = Path(self.reports_dir)
        path = path if path.is_absolute() else ROOT_DIR / path
        try:
            path.mkdir(parents=True, exist_ok=True)
            return path
        except Exception:
            tmp_path = Path("/tmp") / self.reports_dir
            tmp_path.mkdir(parents=True, exist_ok=True)
            return tmp_path


    @property
    def cors_origins(self):
        return [self.frontend_url, 'http://localhost:5173', 'http://localhost:3000']

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
