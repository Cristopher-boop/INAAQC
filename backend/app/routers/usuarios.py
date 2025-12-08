from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.usuarios import Usuario
from app.schemas.usuarios import UsuarioCreate, UsuarioRead
from passlib.context import CryptContext
import uuid

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ------------------------------
# CREATE (POST)
# ------------------------------
@router.post("/", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
async def crear_usuario(data: UsuarioCreate, db: AsyncSession = Depends(get_db)):
    # verificar duplicado
    q = await db.execute(select(Usuario).where(Usuario.nombre_usuario == data.nombre_usuario))
    existing = q.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Ese nombre de usuario ya existe")

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

    return UsuarioRead(
        id_usuario=str(nuevo.id_usuario),
        nombre_usuario=nuevo.nombre_usuario,
        nombre_completo=nuevo.nombre_completo,
        correo_electronico=nuevo.correo_electronico
    )


# ------------------------------
# READ ALL (GET)
# ------------------------------
@router.get("/", response_model=list[UsuarioRead])
async def listar_usuarios(db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(Usuario))
    rows = q.scalars().all()

    return [
        UsuarioRead(
            id_usuario=str(r.id_usuario),
            nombre_usuario=r.nombre_usuario,
            nombre_completo=r.nombre_completo,
            correo_electronico=r.correo_electronico,
        )
        for r in rows
    ]


# ------------------------------
# READ BY ID (GET)
# ------------------------------
@router.get("/{user_id}", response_model=UsuarioRead)
async def obtener_usuario(user_id: str, db: AsyncSession = Depends(get_db)):
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="UUID inválido")

    q = await db.execute(select(Usuario).where(Usuario.id_usuario == uid))
    usuario = q.scalar_one_or_none()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return UsuarioRead(
        id_usuario=str(usuario.id_usuario),
        nombre_usuario=usuario.nombre_usuario,
        nombre_completo=usuario.nombre_completo,
        correo_electronico=usuario.correo_electronico,
    )


# ------------------------------
# UPDATE (PUT)
# ------------------------------
@router.put("/{user_id}", response_model=UsuarioRead)
async def actualizar_usuario(user_id: str, data: UsuarioCreate, db: AsyncSession = Depends(get_db)):
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="UUID inválido")

    q = await db.execute(select(Usuario).where(Usuario.id_usuario == uid))
    usuario = q.scalar_one_or_none()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # actualizar campos
    usuario.nombre_usuario = data.nombre_usuario
    usuario.nombre_completo = data.nombre_completo
    usuario.correo_electronico = data.correo_electronico
    usuario.contraseña_hash = pwd_context.hash(data.contraseña)

    await db.commit()
    await db.refresh(usuario)

    return UsuarioRead(
        id_usuario=str(usuario.id_usuario),
        nombre_usuario=usuario.nombre_usuario,
        nombre_completo=usuario.nombre_completo,
        correo_electronico=usuario.correo_electronico
    )


# ------------------------------
# DELETE (DELETE)
# ------------------------------
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_usuario(user_id: str, db: AsyncSession = Depends(get_db)):
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="UUID inválido")

    q = await db.execute(select(Usuario).where(Usuario.id_usuario == uid))
    usuario = q.scalar_one_or_none()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    await db.delete(usuario)
    await db.commit()

    return None