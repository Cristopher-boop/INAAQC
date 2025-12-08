from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.core.database import get_db
from app.models.tipos_observacion import TipoObservacion
from app.schemas.tipos_observacion import (
    TipoObservacionRead,
    TipoObservacionCreate,
    TipoObservacionUpdate
)

router = APIRouter(prefix="/tipos-observacion", tags=["Tipos de observación"])

# Crear
@router.post("/", response_model=TipoObservacionRead)
async def crear_tipo_observacion(
    data: TipoObservacionCreate,
    db: AsyncSession = Depends(get_db)
):
    obj = TipoObservacion(**data.dict())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


# Listar todos
@router.get("/", response_model=list[TipoObservacionRead])
async def listar_tipos_observacion(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TipoObservacion))
    return result.scalars().all()


# Obtener uno
@router.get("/{id_tipo_obs}", response_model=TipoObservacionRead)
async def obtener_tipo_observacion(id_tipo_obs: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TipoObservacion).where(TipoObservacion.id_tipo_obs == id_tipo_obs)
    )
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Tipo de observación no encontrado")
    return obj


# Eliminar
@router.delete("/{id_tipo_obs}")
async def eliminar_tipo_observacion(id_tipo_obs: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TipoObservacion).where(TipoObservacion.id_tipo_obs == id_tipo_obs)
    )
    obj = result.scalar_one_or_none()

    if not obj:
        raise HTTPException(status_code=404, detail="Tipo de observación no encontrado")

    await db.delete(obj)
    await db.commit()
    return {"detail": "Tipo de observación eliminado correctamente"}

# --------------------------
# PUT - modificar tipo
# --------------------------
@router.put("/{id_tipo_obs}", response_model=TipoObservacionRead)
async def update_tipo_observacion(
    id_tipo_obs: UUID,
    data: TipoObservacionUpdate,
    db: AsyncSession = Depends(get_db)
):
    consulta = select(TipoObservacion).where(TipoObservacion.id_tipo_obs == id_tipo_obs)
    result = await db.execute(consulta)
    registro = result.scalar_one_or_none()

    if registro is None:
        raise HTTPException(status_code=404, detail="Tipo de observación no encontrado")

    # Actualizar solo los campos enviados
    if data.codigo is not None:
        registro.codigo = data.codigo

    if data.nombre is not None:
        registro.nombre = data.nombre

    if data.categoria is not None:
        registro.categoria = data.categoria

    if data.unidad_default is not None:
        registro.unidad_default = data.unidad_default

    await db.commit()
    await db.refresh(registro)

    return registro
