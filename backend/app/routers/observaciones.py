# app/routers/observaciones.py
from fastapi import Query
from sqlalchemy import and_
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.schemas.observaciones import (
    ObservacionCreate, ObservacionUpdate, ObservacionOut
)
from app.models.observaciones import Observacion
from app.core.database import get_db

router = APIRouter(prefix="/observaciones", tags=["Observaciones"])

# --------------------------------------------------
# OBTENER POR ID
# --------------------------------------------------
@router.get("/{id_observacion}", response_model=ObservacionOut)
async def obtener_observacion(
    id_observacion: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Observacion).where(Observacion.id_observacion == id_observacion)
    )
    obs = result.scalar_one_or_none()

    if obs is None:
        raise HTTPException(status_code=404, detail="Observación no encontrada")

    return obs

@router.post("/", response_model=ObservacionOut)
async def crear_observacion(data: ObservacionCreate, db: AsyncSession = Depends(get_db)):
    nueva = Observacion(**data.dict())
    db.add(nueva)
    await db.commit()
    await db.refresh(nueva)
    return nueva


@router.get("/", response_model=list[ObservacionOut])
async def listar_observaciones(
    id_paciente: UUID | None = None,
    id_admision: UUID | None = None,
    id_tipo_obs: UUID | None = None,
    id_archivo: UUID | None = None,
    id_ocr: UUID | None = None,

    creado_inicio: datetime | None = Query(None),
    creado_fin: datetime | None = Query(None),

    fecha_hora_inicio: datetime | None = Query(None),
    fecha_hora_fin: datetime | None = Query(None),

    valor_numerico_inicio: float | None = None,
    valor_numerico_fin: float | None = None,

    valor_texto: str | None = None,
    unidad: str | None = None,

    db: AsyncSession = Depends(get_db)
):
    stmt = select(Observacion)
    filtros = []

    # ---------------- VALIDACIONES DE RANGO ----------------
    def validar_rango(inicio, fin, nombre):
        if inicio and not fin:
            raise HTTPException(
                status_code=400,
                detail=f"Debe especificar el valor final para el rango de {nombre}"
            )
        if fin and not inicio:
            raise HTTPException(
                status_code=400,
                detail=f"Debe especificar el valor inicial para el rango de {nombre}"
            )

    validar_rango(creado_inicio, creado_fin, "creado_en")
    validar_rango(fecha_hora_inicio, fecha_hora_fin, "fecha_hora")
    validar_rango(valor_numerico_inicio, valor_numerico_fin, "valor_numerico")

    # ---------------- FILTROS DIRECTOS ----------------
    if id_paciente:
        filtros.append(Observacion.id_paciente == id_paciente)

    if id_admision:
        filtros.append(Observacion.id_admision == id_admision)

    if id_tipo_obs:
        filtros.append(Observacion.id_tipo_obs == id_tipo_obs)

    if id_archivo:
        filtros.append(Observacion.id_archivo == id_archivo)

    if id_ocr:
        filtros.append(Observacion.id_ocr == id_ocr)

    # ---------------- FILTROS POR RANGO ----------------
    if creado_inicio and creado_fin:
        filtros.append(
            Observacion.creado_en.between(creado_inicio, creado_fin)
        )

    if fecha_hora_inicio and fecha_hora_fin:
        filtros.append(
            Observacion.fecha_hora.between(fecha_hora_inicio, fecha_hora_fin)
        )

    if valor_numerico_inicio and valor_numerico_fin:
        filtros.append(
            Observacion.valor_numerico.between(
                valor_numerico_inicio,
                valor_numerico_fin
            )
        )

    # ---------------- FILTROS DE TEXTO ----------------
    if valor_texto:
        filtros.append(
            Observacion.valor_texto.ilike(f"%{valor_texto}%")
        )

    if unidad:
        filtros.append(
            Observacion.unidad.ilike(f"%{unidad}%")
        )

    if filtros:
        stmt = stmt.where(and_(*filtros))

    result = await db.execute(stmt)
    return result.scalars().all()



@router.put("/{id_observacion}", response_model=ObservacionOut)
async def actualizar_observacion(id_observacion: str, data: ObservacionUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Observacion).where(Observacion.id_observacion == id_observacion))
    obs = result.scalar()

    if not obs:
        raise HTTPException(status_code=404, detail="Observación no encontrada")

    for k, v in data.dict(exclude_unset=True).items():
        setattr(obs, k, v)

    await db.commit()
    await db.refresh(obs)
    return obs

@router.delete("/{id_observacion}")
async def eliminar_observacion(id_observacion: str, db: AsyncSession = Depends(get_db)):

    # Buscar si existe
    result = await db.execute(
        select(Observacion).where(Observacion.id_observacion == id_observacion)
    )
    obs = result.scalar()

    if not obs:
        raise HTTPException(status_code=404, detail="Observación no encontrada")

    # Eliminar
    await db.delete(obs)
    await db.commit()

    return {"detail": "Observación eliminada correctamente"}
