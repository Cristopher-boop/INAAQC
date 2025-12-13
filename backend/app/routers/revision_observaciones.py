# app/routers/revision_observaciones.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from datetime import datetime
from uuid import UUID

from app.core.database import get_db
from app.models.revision_observaciones import RevisionObservacion
from app.schemas.revision_observaciones import (
    RevisionObsCreate, RevisionObsUpdate, RevisionObsOut
)

router = APIRouter(
    prefix="/revision_observaciones",
    tags=["Revisión Observaciones"]
)

# ============================
# CREATE
# ============================
@router.post("/", response_model=RevisionObsOut)
async def crear_revision(
    data: RevisionObsCreate,
    db: AsyncSession = Depends(get_db)
):
    # Validar duplicado por observación
    existe = await db.execute(
        select(RevisionObservacion)
        .where(RevisionObservacion.id_observacion == data.id_observacion)
    )
    if existe.scalar():
        raise HTTPException(
            status_code=400,
            detail="Ya existe una revisión para esta observación"
        )

    nueva = RevisionObservacion(
        id_observacion=data.id_observacion,
        id_usuario_revisor=data.id_usuario_revisor,
        comentarios=data.comentarios,
        estado_revision="pendiente"
    )

    db.add(nueva)
    await db.commit()
    await db.refresh(nueva)
    return nueva


# ============================
# GET BY ID
# ============================
@router.get("/{id_revision}", response_model=RevisionObsOut)
async def obtener_revision(
    id_revision: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(RevisionObservacion)
        .where(RevisionObservacion.id_revision == id_revision)
    )
    rev = result.scalar()

    if not rev:
        raise HTTPException(status_code=404, detail="Revisión no encontrada")

    return rev


# ============================
# LIST + FILTERS
# ============================
@router.get("/", response_model=list[RevisionObsOut])
async def listar_revisiones(
    id_observacion: UUID | None = None,
    id_usuario_revisor: UUID | None = None,
    estado_revision: str | None = None,
    comentarios: str | None = None,
    revisado_desde: datetime | None = Query(None),
    revisado_hasta: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db)
):
    if (revisado_desde and not revisado_hasta) or (revisado_hasta and not revisado_desde):
        raise HTTPException(
            status_code=400,
            detail="Debe especificar ambas fechas: revisado_desde y revisado_hasta"
        )

    if revisado_desde and revisado_hasta and revisado_hasta < revisado_desde:
        raise HTTPException(
            status_code=400,
            detail="La fecha final no puede ser menor a la fecha inicial"
        )

    condiciones = []

    if id_observacion:
        condiciones.append(RevisionObservacion.id_observacion == id_observacion)

    if id_usuario_revisor:
        condiciones.append(RevisionObservacion.id_usuario_revisor == id_usuario_revisor)

    if estado_revision:
        condiciones.append(RevisionObservacion.estado_revision == estado_revision)

    if comentarios:
        condiciones.append(RevisionObservacion.comentarios.ilike(f"%{comentarios}%"))

    if revisado_desde and revisado_hasta:
        condiciones.append(
            RevisionObservacion.revisado_en.between(
                revisado_desde, revisado_hasta
            )
        )

    stmt = select(RevisionObservacion)
    if condiciones:
        stmt = stmt.where(and_(*condiciones))

    result = await db.execute(stmt)
    return result.scalars().all()


# ============================
# UPDATE (SOLO ESTADO)
# ============================
@router.put("/{id_revision}", response_model=RevisionObsOut)
async def actualizar_revision(
    id_revision: UUID,
    data: RevisionObsUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(RevisionObservacion)
        .where(RevisionObservacion.id_revision == id_revision)
    )
    rev = result.scalar()

    if not rev:
        raise HTTPException(status_code=404, detail="Revisión no encontrada")

    if rev.estado_revision != "pendiente":
        raise HTTPException(
            status_code=400,
            detail="La revisión ya fue finalizada y no puede modificarse"
        )

    if data.estado_revision not in {"revisado", "rechazado"}:
        raise HTTPException(
            status_code=400,
            detail="El estado solo puede ser 'revisado' o 'rechazado'"
        )

    rev.estado_revision = data.estado_revision
    rev.revisado_en = datetime.utcnow()

    await db.commit()
    await db.refresh(rev)
    return rev


# ============================
# DELETE (FÍSICO)
# ============================
@router.delete("/{id_revision}")
async def eliminar_revision(
    id_revision: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(RevisionObservacion)
        .where(RevisionObservacion.id_revision == id_revision)
    )
    rev = result.scalar()

    if not rev:
        raise HTTPException(status_code=404, detail="Revisión no encontrada")

    await db.delete(rev)
    await db.commit()

    return {"detail": "Revisión eliminada correctamente"}
