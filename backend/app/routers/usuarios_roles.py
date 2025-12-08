from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db

from app.models.usuarios_roles import UsuariosRoles
from app.schemas.usuarios_roles import UsuarioRolCreate, UsuarioRolResponse

router = APIRouter(
    prefix="/usuarios-roles",
    tags=["Usuarios - Roles"]
)

# Crear relación usuario ↔ rol
@router.post("/", response_model=UsuarioRolResponse)
async def asignar_rol(datos: UsuarioRolCreate, db: AsyncSession = Depends(get_db)):

    # Verificar que no exista relación duplicada
    query = await db.execute(
        select(UsuariosRoles).where(
            UsuariosRoles.id_usuario == datos.id_usuario,
            UsuariosRoles.id_rol == datos.id_rol
        )
    )
    existente = query.scalar_one_or_none()

    if existente:
        raise HTTPException(status_code=400, detail="La relación usuario-rol ya existe.")

    nueva_relacion = UsuariosRoles(
        id_usuario=datos.id_usuario,
        id_rol=datos.id_rol
    )

    db.add(nueva_relacion)
    await db.commit()
    await db.refresh(nueva_relacion)

    return nueva_relacion


# Listar todos los roles asignados
@router.get("/", response_model=list[UsuarioRolResponse])
async def listar_asignaciones(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UsuariosRoles))
    return result.scalars().all()


# Eliminar una asignación
@router.delete("/", status_code=204)
async def eliminar_asignacion(id_usuario: str, id_rol: int, db: AsyncSession = Depends(get_db)):

    query = await db.execute(
        select(UsuariosRoles).where(
            UsuariosRoles.id_usuario == id_usuario,
            UsuariosRoles.id_rol == id_rol
        )
    )
    relacion = query.scalar_one_or_none()

    if not relacion:
        raise HTTPException(status_code=404, detail="Relación no encontrada.")

    await db.delete(relacion)
    await db.commit()

    return
