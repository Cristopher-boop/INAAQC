# app/routers/admisiones.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.models.admisiones import Admision
from app.schemas.admisiones import (
    AdmisionRead,
    AdmisionCreate,
    AdmisionUpdate
)

router = APIRouter(prefix="/admisiones", tags=["Admisiones"])


# --------------------------------------------------
# LISTAR + FILTROS
# --------------------------------------------------
@router.get("/", response_model=list[AdmisionRead])
async def listar_admisiones(
    id_paciente: UUID | None = None,
    diagnostico_principal: str | None = None,
    estado: str | None = None,
    fecha_ingreso_inicio: datetime | None = Query(None),
    fecha_ingreso_fin: datetime | None = Query(None),
    fecha_salida_inicio: datetime | None = Query(None),
    fecha_salida_fin: datetime | None = Query(None),
    creado_inicio: datetime | None = Query(None),
    creado_fin: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Admision)
    filtros = []
    if fecha_ingreso_inicio and not fecha_ingreso_fin:
        raise HTTPException(
            status_code=400,
            detail="Debe especificar la fecha de fin para el rango de fecha_ingreso"
        )

    if fecha_salida_inicio and not fecha_salida_fin:
        raise HTTPException(
            status_code=400,
            detail="Debe especificar la fecha de fin para el rango de fecha_salida"
        )

    if creado_inicio and not creado_fin:
        raise HTTPException(
            status_code=400,
            detail="Debe especificar la fecha de fin para el rango de creado_en"
        )

    if id_paciente:
        filtros.append(Admision.id_paciente == id_paciente)

    if diagnostico_principal:
        filtros.append(Admision.diagnostico_principal.ilike(f"%{diagnostico_principal}%"))

    if estado:
        filtros.append(Admision.estado == estado)

    if fecha_ingreso_inicio and fecha_ingreso_fin:
        filtros.append(Admision.fecha_ingreso.between(fecha_ingreso_inicio, fecha_ingreso_fin))

    if fecha_salida_inicio and fecha_salida_fin:
        filtros.append(Admision.fecha_salida.between(fecha_salida_inicio, fecha_salida_fin))

    if creado_inicio and creado_fin:
        filtros.append(Admision.creado_en.between(creado_inicio, creado_fin))

    if filtros:
        stmt = stmt.where(and_(*filtros))

    result = await db.execute(stmt)
    return result.scalars().all()


# --------------------------------------------------
# OBTENER POR ID
# --------------------------------------------------
@router.get("/{id_admision}", response_model=AdmisionRead)
async def obtener_admision(id_admision: UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(Admision).where(Admision.id_admision == id_admision)
    result = await db.execute(stmt)
    registro = result.scalar_one_or_none()

    if registro is None:
        raise HTTPException(404, "Admisión no encontrada")

    return registro


# --------------------------------------------------
# CREAR (estado siempre activo)
# --------------------------------------------------
@router.post("/", response_model=AdmisionRead)
async def crear_admision(data: AdmisionCreate, db: AsyncSession = Depends(get_db)):

    if data.fecha_salida and data.fecha_ingreso > data.fecha_salida:
        raise HTTPException(
            status_code=400,
            detail="La fecha de ingreso no puede ser posterior a la fecha de salida"
        )

    nueva = Admision(**data.dict())
    db.add(nueva)
    await db.commit()
    await db.refresh(nueva)
    return nueva


# --------------------------------------------------
# ACTUALIZAR (sin cambiar estado)
# --------------------------------------------------
@router.put("/{id_admision}", response_model=AdmisionRead)
async def actualizar_admision(
    id_admision: UUID,
    data: AdmisionUpdate,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Admision).where(Admision.id_admision == id_admision)
    result = await db.execute(stmt)
    registro = result.scalar_one_or_none()

    if registro is None:
        raise HTTPException(404, "Admisión no encontrada")

    # -------- VALIDACIÓN DE FECHAS --------
    fecha_ingreso = data.fecha_ingreso or registro.fecha_ingreso
    fecha_salida = data.fecha_salida or registro.fecha_salida

    if fecha_salida and fecha_ingreso > fecha_salida:
        raise HTTPException(
            status_code=400,
            detail="La fecha de ingreso no puede ser posterior a la fecha de salida"
        )

    for campo, valor in data.dict(exclude_unset=True).items():
        setattr(registro, campo, valor)

    await db.commit()
    await db.refresh(registro)
    return registro


# --------------------------------------------------
# BAJA LÓGICA
# --------------------------------------------------
@router.delete("/{id_admision}")
async def baja_logica_admision(id_admision: UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(Admision).where(Admision.id_admision == id_admision)
    result = await db.execute(stmt)
    registro = result.scalar_one_or_none()

    if registro is None:
        raise HTTPException(404, "Admisión no encontrada")

    if registro.estado == "inactivo":
        raise HTTPException(400, "La admisión ya está inactiva")

    registro.estado = "inactivo"
    await db.commit()

    return {"detail": "Admisión dada de baja correctamente"}

# --------------------------------------------------
# REACTIVAR (estado = "activo")
# --------------------------------------------------
@router.patch("/{id_admision}/activar")
async def reactivar_admision(id_admision: UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(Admision).where(Admision.id_admision == id_admision)
    result = await db.execute(stmt)
    registro = result.scalar_one_or_none()

    if registro is None:
        raise HTTPException(404, "Admisión no encontrada")

    if registro.estado == "activo":
        raise HTTPException(
            status_code=400,
            detail="La admisión ya se encuentra activa"
        )

    registro.estado = "activo"
    await db.commit()

    return {"detail": "Admisión reactivada correctamente"}
