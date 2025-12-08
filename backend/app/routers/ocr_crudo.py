from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.ocr_crudo import OCRCrudo
from app.schemas.ocr_crudo import (
    OCRCrudoCreate,
    OCRCrudoUpdate,
    OCRCrudoResponse
)

router = APIRouter(prefix="/ocr-crudo", tags=["OCR crudo"])


# ⭐ CREATE
@router.post("/", response_model=OCRCrudoResponse)
async def crear_ocr_crudo(data: OCRCrudoCreate, db: AsyncSession = Depends(get_db)):
    nuevo = OCRCrudo(**data.dict())
    db.add(nuevo)
    await db.commit()
    await db.refresh(nuevo)
    return nuevo


# ⭐ READ ALL
@router.get("/", response_model=list[OCRCrudoResponse])
async def listar_ocr_crudo(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(OCRCrudo))
    return result.scalars().all()


# ⭐ READ BY ID
@router.get("/{id_ocr}", response_model=OCRCrudoResponse)
async def obtener_ocr_crudo(id_ocr: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(OCRCrudo).where(OCRCrudo.id_ocr == id_ocr))
    ocr = result.scalar_one_or_none()

    if not ocr:
        raise HTTPException(status_code=404, detail="OCR no encontrado")

    return ocr


# ⭐ UPDATE
@router.put("/{id_ocr}", response_model=OCRCrudoResponse)
async def actualizar_ocr_crudo(id_ocr: str, data: OCRCrudoUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(OCRCrudo).where(OCRCrudo.id_ocr == id_ocr))
    ocr = result.scalar_one_or_none()

    if not ocr:
        raise HTTPException(status_code=404, detail="OCR no encontrado")

    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(ocr, key, value)


    await db.commit()
    await db.refresh(ocr)
    return ocr


# ⭐ DELETE
@router.delete("/{id_ocr}")
async def eliminar_ocr_crudo(id_ocr: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(OCRCrudo).where(OCRCrudo.id_ocr == id_ocr))
    ocr = result.scalar_one_or_none()

    if not ocr:
        raise HTTPException(status_code=404, detail="OCR no encontrado")

    await db.delete(ocr)
    await db.commit()

    return {"detail": "OCR eliminado"}
