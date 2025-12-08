from sqlalchemy import Column, Integer, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class OCRCrudo(Base):
    __tablename__ = "ocr_crudo"

    id_ocr = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_archivo = Column(UUID(as_uuid=True), ForeignKey("archivos.id_archivo"))
    pagina = Column(Integer)
    texto = Column(Text)

    # nombre de la columna sigue siendo "metadata"
    metadata_json = Column("metadata", JSON)

    creado_en = Column(TIMESTAMP(timezone=True), server_default=func.now())