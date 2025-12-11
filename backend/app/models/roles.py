# app/models/roles.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class Rol(Base):
    __tablename__ = "roles"

    id_rol = Column(Integer, primary_key=True, index=True)
    nombre_rol = Column(String, unique=True, nullable=False)

    usuarios = relationship("UsuariosRoles", back_populates="rol")
