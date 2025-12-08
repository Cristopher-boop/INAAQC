# app/routers/pacientes.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update as sql_update, delete as sql_delete
from uuid import UUID as UUID_type
from typing import List, Optional

from app.core.database import get_db
from app.models.pacientes import Paciente
from app.schemas.pacientes import PacienteCreate, PacienteUpdate, PacienteOut

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])


# Crear paciente
@router.post("/", response_model=PacienteOut, status_code=status.HTTP_201_CREATED)
async def crear_paciente(data: PacienteCreate, db: AsyncSession = Depends(get_db)):
    nuevo = Paciente(
        id_externo=data.id_externo,
        nombre=data.nombre,
        apellido=data.apellido,
        fecha_nacimiento=data.fecha_nacimiento,
        sexo=data.sexo
    )
    db.add(nuevo)
    await db.commit()
    await db.refresh(nuevo)
    return nuevo


# Listar pacientes con filtros básicos y paginación
@router.get("/", response_model=List[PacienteOut])
async def listar_pacientes(
    db: AsyncSession = Depends(get_db),
    nombre: Optional[str] = Query(None, description="Filtro por nombre (coincidencia parcial)"),
    apellido: Optional[str] = Query(None, description="Filtro por apellido (coincidencia parcial)"),
    id_externo: Optional[str] = Query(None, description="Filtro por id_externo exacto"),
    limite: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    stmt = select(Paciente)

    if nombre:
        stmt = stmt.where(Paciente.nombre.ilike(f"%{nombre}%"))
    if apellido:
        stmt = stmt.where(Paciente.apellido.ilike(f"%{apellido}%"))
    if id_externo:
        stmt = stmt.where(Paciente.id_externo == id_externo)

    stmt = stmt.offset(offset).limit(limite)

    result = await db.execute(stmt)
    rows = result.scalars().all()
    return rows


# Obtener paciente por ID
@router.get("/{id_paciente}", response_model=PacienteOut)
async def obtener_paciente(id_paciente: UUID_type, db: AsyncSession = Depends(get_db)):
    stmt = select(Paciente).where(Paciente.id_paciente == id_paciente)
    r = await db.execute(stmt)
    paciente = r.scalar_one_or_none()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return paciente


# Actualizar paciente (PUT: reemplaza campos, usa PacienteUpdate para parcial)
@router.put("/{id_paciente}", response_model=PacienteOut)
async def actualizar_paciente(id_paciente: UUID_type, data: PacienteUpdate, db: AsyncSession = Depends(get_db)):
    # obtener primero
    stmt = select(Paciente).where(Paciente.id_paciente == id_paciente)
    r = await db.execute(stmt)
    paciente = r.scalar_one_or_none()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # aplicar cambios solo en campos enviados
    for key, value in data.dict(exclude_unset=True).items():
        setattr(paciente, key, value)

    await db.commit()
    await db.refresh(paciente)
    return paciente


# Eliminar paciente
@router.delete("/{id_paciente}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_paciente(id_paciente: UUID_type, db: AsyncSession = Depends(get_db)):
    stmt = select(Paciente).where(Paciente.id_paciente == id_paciente)
    r = await db.execute(stmt)
    paciente = r.scalar_one_or_none()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    await db.delete(paciente)
    await db.commit()
    return None
