# app/routers/diagnosticos_secundarios.py
from pydantic import BaseModel
from uuid import UUID

# --- Base ---
class DiagnosticoSecundarioBase(BaseModel):
    id_admision: UUID
    diagnostico: str


class DiagnosticoSecundarioCreate(DiagnosticoSecundarioBase):
    pass


class DiagnosticoSecundarioUpdate(BaseModel):
    diagnostico: str | None = None


class DiagnosticoSecundarioOut(DiagnosticoSecundarioBase):
    id_diag_sec: UUID
    estado: str

    model_config = {"from_attributes": True}
