from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class ObservacionBase(BaseModel):
    id_paciente: Optional[UUID] = None
    id_admision: Optional[UUID] = None
    id_tipo_obs: Optional[UUID] = None
    fecha_hora: datetime
    valor_numerico: Optional[float] = None
    valor_texto: Optional[str] = None
    unidad: Optional[str] = None
    id_archivo: Optional[UUID] = None
    id_ocr: Optional[UUID] = None

class ObservacionCreate(ObservacionBase):
    pass

class ObservacionUpdate(ObservacionBase):
    pass

class ObservacionOut(ObservacionBase):
    id_observacion: UUID
    creado_en: datetime

    class Config:
        from_attributes = True
