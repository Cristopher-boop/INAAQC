from pydantic import BaseModel
from uuid import UUID
from typing import Optional, Dict, Any


class OCRCrudoBase(BaseModel):
    id_archivo: UUID
    pagina: int
    texto: str
    metadata_json: Optional[Dict[str, Any]] = None


class OCRCrudoCreate(OCRCrudoBase):
    pass


class OCRCrudoUpdate(BaseModel):
    pagina: Optional[int] = None
    texto: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None


class OCRCrudoResponse(OCRCrudoBase):
    id_ocr: UUID

    class Config:
        from_attributes = True
