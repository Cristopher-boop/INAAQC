from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class TipoObservacionBase(BaseModel):
    codigo: str | None = None
    nombre: str
    categoria: str   # 'LAB', 'VIT', 'PUL'
    unidad_default: str | None = None


class TipoObservacionCreate(TipoObservacionBase):
    pass


class TipoObservacionUpdate(BaseModel):
    codigo: str | None = None
    nombre: str | None = None
    categoria: str | None = None
    unidad_default: str | None = None


class TipoObservacionRead(BaseModel):
    id_tipo_obs: UUID
    codigo: str | None
    nombre: str
    categoria: str
    unidad_default: str | None
    creado_en: datetime

    class Config:
        from_attributes = True
