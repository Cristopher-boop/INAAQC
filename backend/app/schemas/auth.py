# app/schemas/auth.py
from pydantic import BaseModel

class LoginRequest(BaseModel):
    correo_electronico: str
    contraseña: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    mensaje: str