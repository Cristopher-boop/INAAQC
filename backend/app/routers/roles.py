from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.models.roles import Rol
from app.schemas.roles import RolCreate, RolUpdate, RolOut

router = APIRouter(prefix="/roles", tags=["Roles"])

# CREATE
@router.post("/", response_model=RolOut, status_code=status.HTTP_201_CREATED)
async def crear_rol(data: RolCreate, db: AsyncSession = Depends(get_db)):
    nuevo = Rol(**data.dict())
    db.add(nuevo)
    try:
        await db.commit()
        await db.refresh(nuevo)
    except Exception:
        await db.rollback()
        raise HTTPException(400, "El rol ya existe o no es válido.")
    return nuevo


# READ - listar roles
@router.get("/", response_model=List[RolOut])
async def listar_roles(
    db: AsyncSession = Depends(get_db),
    nombre: str | None = Query(None)
):
    stmt = select(Rol)
    if nombre:
        stmt = stmt.where(Rol.nombre_rol.ilike(f"%{nombre}%"))

    result = await db.execute(stmt)
    return result.scalars().all()


# READ - obtener uno
@router.get("/{id_rol}", response_model=RolOut)
async def obtener_rol(id_rol: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Rol).where(Rol.id_rol == id_rol)
    q = await db.execute(stmt)
    rol = q.scalar_one_or_none()

    if not rol:
        raise HTTPException(404, "Rol no encontrado")

    return rol


# UPDATE
@router.put("/{id_rol}", response_model=RolOut)
async def actualizar_rol(id_rol: int, data: RolUpdate, db: AsyncSession = Depends(get_db)):
    stmt = select(Rol).where(Rol.id_rol == id_rol)
    q = await db.execute(stmt)
    rol = q.scalar_one_or_none()

    if not rol:
        raise HTTPException(404, "Rol no encontrado")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(rol, key, value)

    await db.commit()
    await db.refresh(rol)
    return rol


# DELETE
@router.delete("/{id_rol}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_rol(id_rol: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Rol).where(Rol.id_rol == id_rol)
    q = await db.execute(stmt)
    rol = q.scalar_one_or_none()

    if not rol:
        raise HTTPException(404, "Rol no encontrado")

    await db.delete(rol)
    await db.commit()
    return None
