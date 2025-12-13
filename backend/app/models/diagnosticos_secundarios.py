# app/models/diagnosticos_secundarios.py
from sqlalchemy import Column, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base

class DiagnosticoSecundario(Base):
    __tablename__ = "diagnosticos_secundarios"

    id_diag_sec = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid()
    )

    id_admision = Column(
        UUID(as_uuid=True),
        ForeignKey("admisiones.id_admision", ondelete="CASCADE"),
        nullable=False
    )

    diagnostico = Column(Text, nullable=False)

    estado = Column(Text, nullable=False, server_default="activo")
