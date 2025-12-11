# app/schemas/usuarios.py
from pydantic import BaseModel, EmailStr
import uuid

class UsuarioBase(BaseModel):
    nombre_usuario: str
    nombre_completo: str
    correo_electronico: EmailStr | None = None

class UsuarioCreate(UsuarioBase):
    contraseña: str
    id_rol: int  # SE AÑADE ESTO

class UsuarioUpdate(UsuarioBase):
    contraseña: str | None = None
    id_rol: int | None = None
    estado: str | None = None

class UsuarioRead(UsuarioBase):
    id_usuario: uuid.UUID
    rol: str
    estado: str

    class Config:
        orm_mode = True
