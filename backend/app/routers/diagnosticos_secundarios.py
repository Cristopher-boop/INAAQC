from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID

from app.core.database import get_db
from app.models.diagnosticos_secundarios import DiagnosticoSecundario
from app.schemas.diagnosticos_secundarios import (
    DiagnosticoSecundarioCreate,
    DiagnosticoSecundarioOut,
    DiagnosticoSecundarioUpdate
)

router = APIRouter(
    prefix="/diagnosticos-secundarios",
    tags=["Diagnósticos secundarios"]
)

# --------------------------------------------------
# LISTAR + FILTROS
# --------------------------------------------------
@router.get("/", response_model=list[DiagnosticoSecundarioOut])
async def listar_diagnosticos_secundarios(
    id_admision: UUID | None = None,
    diagnostico: str | None = None,
    estado: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(DiagnosticoSecundario)
    filtros = []

    if id_admision:
        filtros.append(DiagnosticoSecundario.id_admision == id_admision)

    if diagnostico:
        filtros.append(
            DiagnosticoSecundario.diagnostico.ilike(f"%{diagnostico}%")
        )

    if estado:
        filtros.append(DiagnosticoSecundario.estado == estado)

    if filtros:
        stmt = stmt.where(and_(*filtros))

    result = await db.execute(stmt)
    return result.scalars().all()


# --------------------------------------------------
# OBTENER POR ID
# --------------------------------------------------
@router.get("/{id_diag_sec}", response_model=DiagnosticoSecundarioOut)
async def obtener_diagnostico_secundario(
    id_diag_sec: UUID,
    db: AsyncSession = Depends(get_db)
):
    diag = await db.get(DiagnosticoSecundario, id_diag_sec)
    if not diag:
        raise HTTPException(404, "Diagnóstico secundario no encontrado")
    return diag


# --------------------------------------------------
# CREAR (estado siempre activo)
# --------------------------------------------------
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


# --------------------------------------------------
# ACTUALIZAR (sin estado)
# --------------------------------------------------
@router.put("/{id_diag_sec}", response_model=DiagnosticoSecundarioOut)
async def actualizar_diagnostico_secundario(
    id_diag_sec: UUID,
    data: DiagnosticoSecundarioUpdate,
    db: AsyncSession = Depends(get_db)
):
    diag = await db.get(DiagnosticoSecundario, id_diag_sec)
    if not diag:
        raise HTTPException(404, "Diagnóstico secundario no encontrado")

    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(diag, campo, valor)

    await db.commit()
    await db.refresh(diag)
    return diag


# --------------------------------------------------
# BAJA LÓGICA
# --------------------------------------------------
@router.delete("/{id_diag_sec}")
async def baja_logica_diagnostico_secundario(
    id_diag_sec: UUID,
    db: AsyncSession = Depends(get_db)
):
    diag = await db.get(DiagnosticoSecundario, id_diag_sec)
    if not diag:
        raise HTTPException(404, "Diagnóstico secundario no encontrado")

    if diag.estado == "inactivo":
        raise HTTPException(400, "El diagnóstico ya está inactivo")

    diag.estado = "inactivo"
    await db.commit()

    return {"detail": "Diagnóstico secundario dado de baja correctamente"}


# --------------------------------------------------
# REACTIVAR
# --------------------------------------------------
@router.patch("/{id_diag_sec}/activar")
async def activar_diagnostico_secundario(
    id_diag_sec: UUID,
    db: AsyncSession = Depends(get_db)
):
    diag = await db.get(DiagnosticoSecundario, id_diag_sec)
    if not diag:
        raise HTTPException(404, "Diagnóstico secundario no encontrado")

    if diag.estado == "activo":
        raise HTTPException(400, "El diagnóstico ya está activo")

    diag.estado = "activo"
    await db.commit()

    return {"detail": "Diagnóstico secundario activado correctamente"}
