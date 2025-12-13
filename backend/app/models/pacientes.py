# app/models/pacientes.py
from sqlalchemy import Column, Text, Date, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base

class Paciente(Base):
    __tablename__ = "pacientes"

    id_paciente = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_externo = Column(Text)
    nombre = Column(Text, nullable=False)
    apellido = Column(Text, nullable=False)
    fecha_nacimiento = Column(Date)
    sexo = Column(Text)
    creado_en = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # 🔥 NUEVO CAMPO PARA BAJA LÓGICA
    estado = Column(Text, nullable=False, server_default="activo")
