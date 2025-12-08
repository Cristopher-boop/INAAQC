# app/schemas/pacientes.py
from pydantic import BaseModel
from datetime import date, datetime
from uuid import UUID
from typing import Optional

class PacienteBase(BaseModel):
    id_externo: Optional[str] = None
    nombre: str
    apellido: str
    fecha_nacimiento: Optional[date] = None
    sexo: Optional[str] = None

class PacienteCreate(PacienteBase):
    pass

class PacienteUpdate(BaseModel):
    id_externo: Optional[str] = None
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    sexo: Optional[str] = None

class PacienteOut(PacienteBase):
    id_paciente: UUID | None = None
    creado_en: datetime | None = None

    model_config = {
        "from_attributes": True
    }
