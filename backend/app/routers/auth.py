from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.usuarios import Usuario
from app.schemas.auth import LoginRequest, TokenResponse
from app.core.security import verify_password
from app.core.jwt_config import crear_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(Usuario).where(Usuario.correo_electronico == data.correo_electronico))
    user = result.scalar()

    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    if not verify_password(data.contraseña, user.contraseña_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    access_token = crear_token({
        "sub": str(user.id_usuario),
        "rol": "admin"   # Luego integramos la tabla usuarios_roles
    })

    return TokenResponse(access_token=access_token)
