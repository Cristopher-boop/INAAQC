from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.revision_observaciones import RevisionObservacion
from app.schemas.revision_observaciones import (
    RevisionObsCreate, RevisionObsUpdate, RevisionObsOut
)

router = APIRouter(prefix="/revision_observaciones", tags=["Revisión Observaciones"])


# CREATE
@router.post("/", response_model=RevisionObsOut)
async def crear_revision(data: RevisionObsCreate, db: AsyncSession = Depends(get_db)):
    nueva = RevisionObservacion(**data.dict())
    db.add(nueva)
    await db.commit()
    await db.refresh(nueva)
    return nueva


# GET LIST
@router.get("/", response_model=list[RevisionObsOut])
async def listar_revisiones(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RevisionObservacion))
    return result.scalars().all()


# UPDATE
@router.put("/{id_revision}", response_model=RevisionObsOut)
async def actualizar_revision(id_revision: str, data: RevisionObsUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(RevisionObservacion).where(RevisionObservacion.id_revision == id_revision)
    )
    rev = result.scalar()

    if not rev:
        raise HTTPException(status_code=404, detail="Revisión no encontrada")

    for k, v in data.dict(exclude_unset=True).items():
        setattr(rev, k, v)

    await db.commit()
    await db.refresh(rev)
    return rev


# DELETE
@router.delete("/{id_revision}")
async def eliminar_revision(id_revision: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(RevisionObservacion).where(RevisionObservacion.id_revision == id_revision)
    )
    rev = result.scalar()

    if not rev:
        raise HTTPException(status_code=404, detail="Revisión no encontrada")

    await db.delete(rev)
    await db.commit()

    return {"detail": "Revisión eliminada correctamente"}
