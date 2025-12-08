from sqlalchemy import Column, ForeignKey, Integer
from app.core.database import Base
from sqlalchemy.dialects.postgresql import UUID

class UsuariosRoles(Base):
    __tablename__ = "usuarios_roles"

    id_usuario = Column(UUID(as_uuid=True), ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), primary_key=True)
    id_rol = Column(Integer, ForeignKey("roles.id_rol", ondelete="CASCADE"), primary_key=True)
