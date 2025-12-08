from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class AdmisionBase(BaseModel):
    id_paciente: UUID
    fecha_ingreso: datetime
    fecha_salida: datetime | None = None
    diagnostico_principal: str | None = None


class AdmisionCreate(AdmisionBase):
    pass


class AdmisionUpdate(BaseModel):
    fecha_ingreso: datetime | None = None
    fecha_salida: datetime | None = None
    diagnostico_principal: str | None = None


class AdmisionRead(BaseModel):
    id_admision: UUID
    id_paciente: UUID
    fecha_ingreso: datetime
    fecha_salida: datetime | None
    diagnostico_principal: str | None
    creado_en: datetime

    class Config:
        from_attributes = True
