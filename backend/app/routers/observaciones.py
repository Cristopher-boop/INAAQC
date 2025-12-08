from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.schemas.observaciones import (
    ObservacionCreate, ObservacionUpdate, ObservacionOut
)
from app.models.observaciones import Observacion
from app.core.database import get_db

router = APIRouter(prefix="/observaciones", tags=["Observaciones"])

@router.post("/", response_model=ObservacionOut)
async def crear_observacion(data: ObservacionCreate, db: AsyncSession = Depends(get_db)):
    nueva = Observacion(**data.dict())
    db.add(nueva)
    await db.commit()
    await db.refresh(nueva)
    return nueva


@router.get("/", response_model=list[ObservacionOut])
async def listar_observaciones(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Observacion))
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
