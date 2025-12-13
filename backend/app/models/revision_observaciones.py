# app/models/revision_observaciones.py
from sqlalchemy import Column, ForeignKey, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func, text
from app.core.database import Base

class RevisionObservacion(Base):
    __tablename__ = "revision_observaciones"

    id_revision = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    id_observacion = Column(UUID(as_uuid=True), ForeignKey("observaciones.id_observacion"))
    id_usuario_revisor = Column(UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"))

    estado_revision = Column(
        Text,
        server_default="pendiente"
    )

    comentarios = Column(Text)
    revisado_en = Column(TIMESTAMP(timezone=True))
