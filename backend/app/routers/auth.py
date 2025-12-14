from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.usuarios import Usuario
from app.models.roles import Rol
from app.models.usuarios_roles import UsuariosRoles
from app.schemas.auth import LoginRequest, TokenResponse, UsuarioLoginOut
from app.core.security import verify_password
from app.core.jwt_config import crear_token

router = APIRouter(prefix="/auth", tags=["Auth"])

# ---------------- MENSAJES POR ROL ----------------
ROL_MENSAJES = {
    "superadministrador": "Hola Superadmin!!",
    "doctor": "Hola Doctor!!",
    "analista": "Hola Analista!!",
    "ti": "Hola TI!!"
}

# ---------------- LOGIN ----------------
@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):

    # ----------- BUSCAR USUARIO + ROL -----------
    stmt = (
        select(Usuario, Rol)
        .join(UsuariosRoles, Usuario.id_usuario == UsuariosRoles.id_usuario)
        .join(Rol, Rol.id_rol == UsuariosRoles.id_rol)
        .where(Usuario.correo_electronico == data.correo_electronico)
    )

    row = (await db.execute(stmt)).one_or_none()

    if not row:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    user, rol = row

    # ----------- VALIDACIONES -----------
    if user.estado != "activo":
        raise HTTPException(status_code=403, detail="Usuario inactivo")

    if not verify_password(data.contraseña, user.contraseña_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    # ----------- NORMALIZAR ROL -----------
    rol_key = rol.nombre_rol.strip().lower()
    mensaje = ROL_MENSAJES.get(rol_key)

    if not mensaje:
        raise HTTPException(
            status_code=500,
            detail=f"Rol no reconocido: {rol.nombre_rol}"
        )

    # ----------- TOKEN -----------
    access_token = crear_token({
        "sub": str(user.id_usuario),
        "rol": rol_key
    })

    # ----------- RESPUESTA -----------
    return TokenResponse(
        access_token=access_token,
        mensaje=mensaje,
        usuario=UsuarioLoginOut(
            id_usuario=user.id_usuario,
            nombre_usuario=user.nombre_usuario,
            nombre_completo=user.nombre_completo,
            correo_electronico=user.correo_electronico,
            rol=rol_key
        )
    )
