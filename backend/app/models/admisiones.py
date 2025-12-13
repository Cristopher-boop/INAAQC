# app/models/admisiones.py
from sqlalchemy import Column, Text, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class Admision(Base):
    __tablename__ = "admisiones"

    # Genera un UUID en Python si no se proporciona, y también confía en la DB como fallback
    id_admision = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,          # genera automáticamente en Python si no se pasa
        server_default=func.gen_random_uuid()  # genera en la DB si se inserta directamente
    )

    id_paciente = Column(
        UUID(as_uuid=True),
        ForeignKey("pacientes.id_paciente"),
        nullable=False
    )

    fecha_ingreso = Column(TIMESTAMP(timezone=True), nullable=False)
    fecha_salida = Column(TIMESTAMP(timezone=True), nullable=True)
    diagnostico_principal = Column(Text, nullable=True)
    creado_en = Column(TIMESTAMP(timezone=True), server_default=func.now())
