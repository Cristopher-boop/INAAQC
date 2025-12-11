# app/routers/usuarios.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from passlib.context import CryptContext
import uuid

from app.core.database import get_db
from app.models.usuarios import Usuario
from app.models.roles import Rol
from app.models.usuarios_roles import UsuariosRoles
from app.schemas.usuarios import UsuarioCreate, UsuarioRead, UsuarioUpdate

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================================
# CREATE (POST)
# ============================================================
@router.post("/", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
async def crear_usuario(data: UsuarioCreate, db: AsyncSession = Depends(get_db)):

    # Validar duplicado
    q = await db.execute(select(Usuario).where(Usuario.nombre_usuario == data.nombre_usuario))
    if q.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Ese nombre de usuario ya existe")

    # Validar rol
    q = await db.execute(select(Rol).where(Rol.id_rol == data.id_rol))
    rol = q.scalar_one_or_none()
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    hashed = pwd_context.hash(data.contraseña)

    nuevo = Usuario(
        nombre_usuario=data.nombre_usuario,
        nombre_completo=data.nombre_completo,
        correo_electronico=data.correo_electronico,
        contraseña_hash=hashed,
    )

    db.add(nuevo)
    await db.commit()
    await db.refresh(nuevo)

    # Asignar rol
    asignacion = UsuariosRoles(
        id_usuario=nuevo.id_usuario,
        id_rol=data.id_rol
    )

    db.add(asignacion)
    await db.commit()

    return UsuarioRead(
        id_usuario=nuevo.id_usuario,
        nombre_usuario=nuevo.nombre_usuario,
        nombre_completo=nuevo.nombre_completo,
        correo_electronico=nuevo.correo_electronico,
        estado=nuevo.estado,
        rol=rol.nombre_rol
    )


# ============================================================
# READ ALL (GET)
# ============================================================
@router.get("/", response_model=list[UsuarioRead])
async def listar_usuarios(
    rol: str | None = None,
    nombre: str | None = None,
    correo: str | None = None,
    estado: str | None = None,
    db: AsyncSession = Depends(get_db)
):

    stmt = (
        select(Usuario, Rol)
        .join(UsuariosRoles, Usuario.id_usuario == UsuariosRoles.id_usuario)
        .join(Rol, Rol.id_rol == UsuariosRoles.id_rol)
    )

    # --- Filtros dinámicos ---
    conditions = []

    if rol:
        conditions.append(Rol.nombre_rol == rol)

    if nombre:
        conditions.append(Usuario.nombre_completo.ilike(f"%{nombre}%"))

    if correo:
        conditions.append(Usuario.correo_electronico.ilike(f"%{correo}%"))

    if estado:
        conditions.append(Usuario.estado == estado)

    if conditions:
        stmt = stmt.where(and_(*conditions))

    rows = (await db.execute(stmt)).all()

    return [
        UsuarioRead(
            id_usuario=u.id_usuario,
            nombre_usuario=u.nombre_usuario,
            nombre_completo=u.nombre_completo,
            correo_electronico=u.correo_electronico,
            estado=u.estado,
            rol=r.nombre_rol
        )
        for u, r in rows
    ]


# ============================================================
# READ BY ID
# ============================================================
@router.get("/{user_id}", response_model=UsuarioRead)
async def obtener_usuario(user_id: str, db: AsyncSession = Depends(get_db)):
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="UUID inválido")

    stmt = (
        select(Usuario, Rol)
        .join(UsuariosRoles, Usuario.id_usuario == UsuariosRoles.id_usuario)
        .join(Rol, Rol.id_rol == UsuariosRoles.id_rol)
        .where(Usuario.id_usuario == uid)
    )

    row = (await db.execute(stmt)).one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    u, r = row

    return UsuarioRead(
        id_usuario=u.id_usuario,
        nombre_usuario=u.nombre_usuario,
        nombre_completo=u.nombre_completo,
        correo_electronico=u.correo_electronico,
        estado=u.estado,
        rol=r.nombre_rol
    )


# ============================================================
# UPDATE (PUT)
# ============================================================
@router.put("/{user_id}", response_model=UsuarioRead)
async def actualizar_usuario(user_id: str, data: UsuarioUpdate, db: AsyncSession = Depends(get_db)):

    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="UUID inválido")

    # usuario
    q = await db.execute(select(Usuario).where(Usuario.id_usuario == uid))
    user = q.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # actualizar datos
    user.nombre_usuario = data.nombre_usuario or user.nombre_usuario
    user.nombre_completo = data.nombre_completo or user.nombre_completo
    user.correo_electronico = data.correo_electronico or user.correo_electronico
    user.estado = data.estado or user.estado

    if data.contraseña:
        user.contraseña_hash = pwd_context.hash(data.contraseña)

    # cambio de rol
    if data.id_rol is not None:

        # validar rol
        q = await db.execute(select(Rol).where(Rol.id_rol == data.id_rol))
        rol = q.scalar_one_or_none()
        if not rol:
            raise HTTPException(status_code=404, detail="Rol no encontrado")

        # actualizar relación
        stmt = select(UsuariosRoles).where(UsuariosRoles.id_usuario == uid)
        rel = (await db.execute(stmt)).scalar_one_or_none()

        rel.id_rol = data.id_rol

    await db.commit()
    await db.refresh(user)

    # obtener rol final
    stmt = (
        select(Rol.nombre_rol)
        .join(UsuariosRoles, Rol.id_rol == UsuariosRoles.id_rol)
        .where(UsuariosRoles.id_usuario == uid)
    )
    rol_final = (await db.execute(stmt)).scalar_one()

    return UsuarioRead(
        id_usuario=user.id_usuario,
        nombre_usuario=user.nombre_usuario,
        nombre_completo=user.nombre_completo,
        correo_electronico=user.correo_electronico,
        estado=user.estado,
        rol=rol_final
    )


# ============================================================
# DELETE (ELIMINACIÓN LÓGICA)
# ============================================================
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_usuario(user_id: str, db: AsyncSession = Depends(get_db)):
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="UUID inválido")

    q = await db.execute(select(Usuario).where(Usuario.id_usuario == uid))
    user = q.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # eliminación lógica
    user.estado = "inactivo"

    await db.commit()
    return None
