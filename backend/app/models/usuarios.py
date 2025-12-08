from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String, text
import uuid
from app.core.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    nombre_usuario: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    contraseña_hash: Mapped[str] = mapped_column(String(200), nullable=False)
    nombre_completo: Mapped[str] = mapped_column(String(200), nullable=False)
    correo_electronico: Mapped[str | None] = mapped_column(String(200), nullable=True)
