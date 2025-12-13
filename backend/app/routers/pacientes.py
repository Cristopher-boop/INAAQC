# app/routers/pacientes.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID as UUID_type
from typing import List, Optional
from datetime import date, timedelta

from app.core.database import get_db
from app.models.pacientes import Paciente
from app.schemas.pacientes import PacienteCreate, PacienteUpdate, PacienteOut

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])


# ============================================================
# VALIDACIÓN FECHA NACIMIENTO
# ============================================================
def validar_fecha_nacimiento(fecha: Optional[date]):
    if fecha is None:
        return

    hoy = date.today()

    if fecha > hoy:
        raise HTTPException(
            status_code=400,
            detail="La fecha de nacimiento no puede ser posterior a la fecha actual."
        )

    limite_min = hoy - timedelta(days=30)  # máximo 1 mes de edad

    if fecha > limite_min:
        raise HTTPException(
            status_code=400,
            detail="El paciente debe tener al menos 1 mes de edad para registrarse."
        )


# ============================================================
# Crear paciente
# ============================================================
@router.post("/", response_model=PacienteOut, status_code=status.HTTP_201_CREATED)
async def crear_paciente(data: PacienteCreate, db: AsyncSession = Depends(get_db)):

    validar_fecha_nacimiento(data.fecha_nacimiento)

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


# ============================================================
# Listar pacientes con filtros + paginación + filtro por estado
# incluyendo filtro por fecha_nacimiento (min - max)
# ============================================================
@router.get("/", response_model=List[PacienteOut])
async def listar_pacientes(
    db: AsyncSession = Depends(get_db),
    nombre: Optional[str] = Query(None),
    apellido: Optional[str] = Query(None),
    id_externo: Optional[str] = Query(None),
    estado: Optional[str] = Query(None, description="activo / inactivo"),
    fecha_min: Optional[date] = Query(None),
    fecha_max: Optional[date] = Query(None),
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
    if estado:
        stmt = stmt.where(Paciente.estado == estado)

    if fecha_min:
        stmt = stmt.where(Paciente.fecha_nacimiento >= fecha_min)
    if fecha_max:
        stmt = stmt.where(Paciente.fecha_nacimiento <= fecha_max)

    stmt = stmt.offset(offset).limit(limite)

    result = await db.execute(stmt)
    rows = result.scalars().all()
    return rows


# ============================================================
# Listar solo activos
# ============================================================
@router.get("/activos", response_model=List[PacienteOut])
async def listar_pacientes_activos(db: AsyncSession = Depends(get_db)):
    stmt = select(Paciente).where(Paciente.estado == "activo")
    r = await db.execute(stmt)
    return r.scalars().all()


# ============================================================
# Listar solo inactivos
# ============================================================
@router.get("/inactivos", response_model=List[PacienteOut])
async def listar_pacientes_inactivos(db: AsyncSession = Depends(get_db)):
    stmt = select(Paciente).where(Paciente.estado == "inactivo")
    r = await db.execute(stmt)
    return r.scalars().all()


# ============================================================
# Obtener paciente por ID
# ============================================================
@router.get("/{id_paciente}", response_model=PacienteOut)
async def obtener_paciente(id_paciente: UUID_type, db: AsyncSession = Depends(get_db)):
    stmt = select(Paciente).where(Paciente.id_paciente == id_paciente)
    r = await db.execute(stmt)
    paciente = r.scalar_one_or_none()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return paciente


# ============================================================
# Actualizar paciente (PUT)
# ============================================================
@router.put("/{id_paciente}", response_model=PacienteOut)
async def actualizar_paciente(id_paciente: UUID_type, data: PacienteUpdate, db: AsyncSession = Depends(get_db)):
    stmt = select(Paciente).where(Paciente.id_paciente == id_paciente)
    r = await db.execute(stmt)
    paciente = r.scalar_one_or_none()

    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Validar nueva fecha de nacimiento si la envían
    if data.fecha_nacimiento is not None:
        validar_fecha_nacimiento(data.fecha_nacimiento)

    for key, value in data.dict(exclude_unset=True).items():
        setattr(paciente, key, value)

    await db.commit()
    await db.refresh(paciente)
    return paciente


# ============================================================
# Baja lógica (cambiar estado → inactivo)
# ============================================================
@router.patch("/{id_paciente}/baja", response_model=PacienteOut)
async def baja_logica_paciente(id_paciente: UUID_type, db: AsyncSession = Depends(get_db)):
    stmt = select(Paciente).where(Paciente.id_paciente == id_paciente)
    r = await db.execute(stmt)
    paciente = r.scalar_one_or_none()

    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    if paciente.estado == "inactivo":
        raise HTTPException(
            status_code=400,
            detail="El paciente ya se encuentra inactivo"
        )

    paciente.estado = "inactivo"
    await db.commit()
    await db.refresh(paciente)
    return paciente


# ============================================================
# Eliminación física
# ============================================================
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


# ============================================================
# Reactivar paciente (estado → activo)
# ============================================================
@router.patch("/{id_paciente}/activar", response_model=PacienteOut)
async def reactivar_paciente(id_paciente: UUID_type, db: AsyncSession = Depends(get_db)):
    stmt = select(Paciente).where(Paciente.id_paciente == id_paciente)
    r = await db.execute(stmt)
    paciente = r.scalar_one_or_none()

    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    if paciente.estado == "activo":
        raise HTTPException(
            status_code=400,
            detail="El paciente ya se encuentra activo"
        )

    paciente.estado = "activo"
    await db.commit()
    await db.refresh(paciente)
    return paciente
