from sqlalchemy import Column, Text, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.types import TIMESTAMP
from app.core.database import Base
import uuid


class Archivo(Base):
    __tablename__ = "archivos"

    id_archivo = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre_archivo = Column(Text, nullable=False)
    ruta_almacenamiento = Column(Text, nullable=False)
    tipo_archivo = Column(Text, nullable=False)  # pdf, jpg, png
    tamaño_bytes = Column(BigInteger)
    subido_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"))
    subido_en = Column(TIMESTAMP(timezone=True), server_default=func.now())