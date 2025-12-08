from pydantic import BaseModel, EmailStr
from typing import Optional

class UsuarioBase(BaseModel):
    nombre_usuario: str
    nombre_completo: str
    correo_electronico: Optional[EmailStr] = None

class UsuarioCreate(UsuarioBase):
    contraseña: str

class UsuarioRead(UsuarioBase):
    id_usuario: str

    model_config = {
        "from_attributes": True
    }

class UsuarioResponse(UsuarioBase):
    id_usuario: str

    model_config = {
        "from_attributes": True
    }

