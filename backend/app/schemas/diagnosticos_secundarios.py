from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

# --- Base ---
class DiagnosticoSecundarioBase(BaseModel):
    id_admision: UUID
    diagnostico: str


# --- Create ---
class DiagnosticoSecundarioCreate(DiagnosticoSecundarioBase):
    pass


# --- Update ---
class DiagnosticoSecundarioUpdate(BaseModel):
    diagnostico: str | None = None


# --- Out ---
class DiagnosticoSecundarioOut(DiagnosticoSecundarioBase):
    id_diag_sec: UUID

    model_config = {"from_attributes": True}
