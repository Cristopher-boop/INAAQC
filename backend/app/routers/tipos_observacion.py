# app/routers/tipos_observación.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.models.tipos_observacion import TipoObservacion
from app.schemas.tipos_observacion import (
    TipoObservacionRead,
    TipoObservacionCreate,
    TipoObservacionUpdate
)

router = APIRouter(prefix="/tipos-observacion", tags=["Tipos de observación"])


# --------------------------------------------------------
#   CREAR
# --------------------------------------------------------
@router.post("/", response_model=TipoObservacionRead)
async def crear_tipo_observacion(
    data: TipoObservacionCreate,
    db: AsyncSession = Depends(get_db)
):
    obj = TipoObservacion(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


# --------------------------------------------------------
#   LISTAR + FILTROS
# --------------------------------------------------------
@router.get("/", response_model=list[TipoObservacionRead])
async def listar_tipos_observacion(
    codigo: str | None = None,
    nombre: str | None = None,
    categoria: str | None = None,
    unidad_default: str | None = None,
    estado: str | None = None,
    fecha_inicio: datetime | None = Query(None),
    fecha_fin: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db)
):
    query = select(TipoObservacion)
    filtros = []

    if codigo:
        filtros.append(TipoObservacion.codigo == codigo)

    if nombre:
        filtros.append(TipoObservacion.nombre.ilike(f"%{nombre}%"))

    if categoria:
        filtros.append(TipoObservacion.categoria == categoria)

    if unidad_default:
        filtros.append(TipoObservacion.unidad_default == unidad_default)

    if estado:
        filtros.append(TipoObservacion.estado == estado)

    if fecha_inicio and fecha_fin:
        filtros.append(
            TipoObservacion.creado_en.between(fecha_inicio, fecha_fin)
        )
    elif fecha_inicio:
        filtros.append(TipoObservacion.creado_en >= fecha_inicio)
    elif fecha_fin:
        filtros.append(TipoObservacion.creado_en <= fecha_fin)

    if filtros:
        query = query.where(and_(*filtros))

    result = await db.execute(query)
    return result.scalars().all()


# --------------------------------------------------------
#   OBTENER UNO
# --------------------------------------------------------
@router.get("/{id_tipo_obs}", response_model=TipoObservacionRead)
async def obtener_tipo_observacion(id_tipo_obs: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TipoObservacion).where(TipoObservacion.id_tipo_obs == id_tipo_obs)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Tipo de observación no encontrado")
    return obj


# --------------------------------------------------------
#   ACTUALIZAR
# --------------------------------------------------------
@router.put("/{id_tipo_obs}", response_model=TipoObservacionRead)
async def update_tipo_observacion(
    id_tipo_obs: UUID,
    data: TipoObservacionUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(TipoObservacion).where(TipoObservacion.id_tipo_obs == id_tipo_obs)
    )
    registro = result.scalar_one_or_none()

    if registro is None:
        raise HTTPException(404, "Tipo de observación no encontrado")

    for campo, valor in data.model_dump(exclude_unset=True).items():
        setattr(registro, campo, valor)

    await db.commit()
    await db.refresh(registro)

    return registro


# --------------------------------------------------------
#   BAJA LÓGICA  (estado = "inactivo")
# --------------------------------------------------------
@router.delete("/{id_tipo_obs}")
async def baja_logica_tipo_observacion(id_tipo_obs: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TipoObservacion).where(TipoObservacion.id_tipo_obs == id_tipo_obs)
    )
    registro = result.scalar_one_or_none()

    if registro is None:
        raise HTTPException(404, "Tipo de observación no encontrado")

    registro.estado = "inactivo"
    await db.commit()

    return {"detail": "Tipo de observación desactivado correctamente"}
