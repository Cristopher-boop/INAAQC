from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.core.database import get_db
from app.models.diagnosticos_secundarios import DiagnosticoSecundario
from app.schemas.diagnosticos_secundarios import (
    DiagnosticoSecundarioCreate,
    DiagnosticoSecundarioOut,
    DiagnosticoSecundarioUpdate
)

router = APIRouter(prefix="/diagnosticos_secundarios", tags=["Diagnósticos secundarios"])


# --- CREATE ---
@router.post("/", response_model=DiagnosticoSecundarioOut)
async def crear_diagnostico_secundario(
    data: DiagnosticoSecundarioCreate,
    db: AsyncSession = Depends(get_db)
):
    nuevo = DiagnosticoSecundario(**data.model_dump())
    db.add(nuevo)
    await db.commit()
    await db.refresh(nuevo)
    return nuevo


# --- LISTAR POR ADMISION ---
@router.get("/admision/{id_admision}", response_model=list[DiagnosticoSecundarioOut])
async def obtener_por_admision(id_admision: UUID, db: AsyncSession = Depends(get_db)):
    query = select(DiagnosticoSecundario).where(DiagnosticoSecundario.id_admision == id_admision)
    result = await db.execute(query)
    return result.scalars().all()


# --- OBTENER UNO ---
@router.get("/{id_diag_sec}", response_model=DiagnosticoSecundarioOut)
async def obtener_diagnostico(id_diag_sec: UUID, db: AsyncSession = Depends(get_db)):
    diag = await db.get(DiagnosticoSecundario, id_diag_sec)
    if not diag:
        raise HTTPException(status_code=404, detail="Diagnóstico secundario no encontrado")
    return diag


# --- UPDATE ---
@router.put("/{id_diag_sec}", response_model=DiagnosticoSecundarioOut)
async def actualizar_diagnostico(
    id_diag_sec: UUID,
    data: DiagnosticoSecundarioUpdate,
    db: AsyncSession = Depends(get_db),
):
    diag = await db.get(DiagnosticoSecundario, id_diag_sec)
    if not diag:
        raise HTTPException(status_code=404, detail="Diagnóstico no encontrado")

    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(diag, key, value)

    db.add(diag)
    await db.commit()
    await db.refresh(diag)
    return diag


# --- DELETE ---
@router.delete("/{id_diag_sec}")
async def eliminar_diagnostico(id_diag_sec: UUID, db: AsyncSession = Depends(get_db)):
    diag = await db.get(DiagnosticoSecundario, id_diag_sec)
    if not diag:
        raise HTTPException(status_code=404, detail="Diagnóstico no encontrado")

    await db.delete(diag)
    await db.commit()

    return {"message": "Diagnóstico secundario eliminado"}
