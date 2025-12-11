# app/models/usuarios_roles.py
from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class UsuariosRoles(Base):
    __tablename__ = "usuarios_roles"

    id_usuario = Column(UUID(as_uuid=True), ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), primary_key=True)
    id_rol = Column(Integer, ForeignKey("roles.id_rol", ondelete="CASCADE"), primary_key=True)

    usuario = relationship("Usuario", back_populates="roles")
    rol = relationship("Rol", back_populates="usuarios")
