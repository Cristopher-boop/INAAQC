from sqlalchemy import Column, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from uuid import uuid4
from datetime import datetime
from app.core.database import Base

class TipoObservacion(Base):
    __tablename__ = "tipos_observacion"

    id_tipo_obs = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    codigo = Column(Text, nullable=True)
    nombre = Column(Text, nullable=False)
    categoria = Column(Text, nullable=False)  # LAB, VIT, PUL
    unidad_default = Column(Text, nullable=True)
    # importante: server_default + python default
    creado_en = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),    # deja que la BD ponga now() si por alguna razón no hay valor en Python
        default=datetime.utcnow       # garantiza valor en el objeto Python antes del INSERT
    )
