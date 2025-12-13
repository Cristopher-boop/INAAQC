# app/models/observaciones.py
from sqlalchemy import Column, ForeignKey, TIMESTAMP, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func, text
from app.core.database import Base

class Observacion(Base):
    __tablename__ = "observaciones"

    id_observacion = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    id_paciente = Column(UUID(as_uuid=True), ForeignKey("pacientes.id_paciente"))
    id_admision = Column(UUID(as_uuid=True), ForeignKey("admisiones.id_admision"))
    id_tipo_obs = Column(UUID(as_uuid=True), ForeignKey("tipos_observacion.id_tipo_obs"))

    fecha_hora = Column(TIMESTAMP(timezone=True), nullable=False)

    valor_numerico = Column(Numeric)
    valor_texto = Column(Text)
    unidad = Column(Text)

    id_archivo = Column(UUID(as_uuid=True), ForeignKey("archivos.id_archivo"))
    id_ocr = Column(UUID(as_uuid=True), ForeignKey("ocr_crudo.id_ocr"))

    creado_en = Column(TIMESTAMP(timezone=True), server_default=func.now())
