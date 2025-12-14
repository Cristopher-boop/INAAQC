from pydantic import BaseModel
from uuid import UUID

# -------------------------
# REQUEST
# -------------------------
class LoginRequest(BaseModel):
    correo_electronico: str
    contraseña: str


# -------------------------
# USER INFO (LOGIN RESPONSE)
# -------------------------
class UsuarioLoginOut(BaseModel):
    id_usuario: UUID
    nombre_usuario: str
    nombre_completo: str
    correo_electronico: str | None
    rol: str


# -------------------------
# TOKEN RESPONSE
# -------------------------
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    mensaje: str
    usuario: UsuarioLoginOut
