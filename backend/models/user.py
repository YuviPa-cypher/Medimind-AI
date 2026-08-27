from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field

Role = Literal['Patient', 'Doctor', 'Admin']

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    role: Role
    password: str = Field(..., min_length=6)
    organization_domain: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    role: Optional[Role] = None

class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    user_id: Optional[str] = None
    name: Optional[str] = None
    role: Optional[str] = None

class UserInDB(UserCreate):
    hashed_password: str
