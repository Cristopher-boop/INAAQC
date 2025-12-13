# app/schemas/revision_observaciones.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class RevisionObsBase(BaseModel):
    id_observacion: Optional[UUID] = None
    id_usuario_revisor: Optional[UUID] = None
    estado_revision: Optional[str] = None
    comentarios: Optional[str] = None
    revisado_en: Optional[datetime] = None

class RevisionObsCreate(RevisionObsBase):
    pass

class RevisionObsUpdate(RevisionObsBase):
    pass

class RevisionObsOut(RevisionObsBase):
    id_revision: UUID

    class Config:
        from_attributes = True
