# app/schemas/archivos.py
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class ArchivoRead(BaseModel):
    id_archivo: UUID
    nombre_archivo: str
    ruta_almacenamiento: str
    tipo_archivo: str
    tamaño_bytes: int
    subido_por: UUID | None
    subido_en: datetime
    estado: str   # 👉 NUEVO

    class Config:
        from_attributes = True


class ArchivoUpdate(BaseModel):
    nombre_archivo: str | None = None
    tipo_archivo: str | None = None
    estado: str | None = None
