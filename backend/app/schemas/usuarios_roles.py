from pydantic import BaseModel
from uuid import UUID

class UsuarioRolBase(BaseModel):
    id_usuario: UUID
    id_rol: int

class UsuarioRolCreate(UsuarioRolBase):
    pass

class UsuarioRolResponse(UsuarioRolBase):
    class Config:
        orm_mode = True
