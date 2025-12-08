from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.core.database import get_db
from app.models.admisiones import Admision
from app.schemas.admisiones import (
    AdmisionRead,
    AdmisionCreate,
    AdmisionUpdate
)

router = APIRouter(prefix="/admisiones", tags=["Admisiones"])


# --------------------------
# GET all
# --------------------------
@router.get("/", response_model=list[AdmisionRead])
async def listar_admisiones(db: AsyncSession = Depends(get_db)):
    consulta = select(Admision)
    result = await db.execute(consulta)
    return result.scalars().all()


# --------------------------
# GET by ID
# --------------------------
@router.get("/{id_admision}", response_model=AdmisionRead)
async def obtener_admision(id_admision: UUID, db: AsyncSession = Depends(get_db)):
    consulta = select(Admision).where(Admision.id_admision == id_admision)
    result = await db.execute(consulta)
    registro = result.scalar_one_or_none()

    if registro is None:
        raise HTTPException(status_code=404, detail="Admisión no encontrada")

    return registro


# --------------------------
# POST
# --------------------------
@router.post("/", response_model=AdmisionRead)
async def crear_admision(data: AdmisionCreate, db: AsyncSession = Depends(get_db)):
    nueva = Admision(**data.dict())

    db.add(nueva)
    await db.commit()
    await db.refresh(nueva)

    return nueva


# --------------------------
# PUT
# --------------------------
@router.put("/{id_admision}", response_model=AdmisionRead)
async def actualizar_admision(
    id_admision: UUID,
    data: AdmisionUpdate,
    db: AsyncSession = Depends(get_db)
):
    consulta = select(Admision).where(Admision.id_admision == id_admision)
    result = await db.execute(consulta)
    registro = result.scalar_one_or_none()

    if registro is None:
        raise HTTPException(status_code=404, detail="Admisión no encontrada")

    if data.fecha_ingreso is not None:
        registro.fecha_ingreso = data.fecha_ingreso
    if data.fecha_salida is not None:
        registro.fecha_salida = data.fecha_salida
    if data.diagnostico_principal is not None:
        registro.diagnostico_principal = data.diagnostico_principal

    await db.commit()
    await db.refresh(registro)

    return registro


# --------------------------
# DELETE
# --------------------------
@router.delete("/{id_admision}")
async def eliminar_admision(id_admision: UUID, db: AsyncSession = Depends(get_db)):
    consulta = select(Admision).where(Admision.id_admision == id_admision)
    result = await db.execute(consulta)
    registro = result.scalar_one_or_none()

    if registro is None:
        raise HTTPException(status_code=404, detail="Admisión no encontrada")

    await db.delete(registro)
    await db.commit()

    return {"message": "Admisión eliminada"}
