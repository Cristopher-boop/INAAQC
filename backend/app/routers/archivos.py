# app/routers/archivos.py
import os
import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.core.database import get_db
from app.models.archivos import Archivo
from app.schemas.archivos import ArchivoRead, ArchivoUpdate
from fastapi.responses import FileResponse

router = APIRouter(prefix="/archivos", tags=["Archivos"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ---------------------------
#   SUBIR ARCHIVO
#   Nota: por ahora aceptamos subido_por opcional; para hacerlo automático
#   hay que extraer el usuario con una dependencia de autenticación.
# ---------------------------
@router.post("/upload", response_model=ArchivoRead)
async def subir_archivo(
    archivo: UploadFile = File(...),
    subido_por: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    ext = archivo.filename.split(".")[-1].lower()
    if ext == "jpeg":
        ext = "jpg"
    if ext not in ("pdf", "jpg", "png"):
        raise HTTPException(400, "Tipo de archivo no permitido (solo pdf,jpg,png)")

    file_uuid = uuid.uuid4()
    internal_name = f"{file_uuid}.{ext}"
    save_path = os.path.join(UPLOAD_DIR, internal_name)

    content = await archivo.read()
    with open(save_path, "wb") as f:
        f.write(content)

    tamaño = os.path.getsize(save_path)

    nuevo = Archivo(
        id_archivo=file_uuid,
        nombre_archivo=archivo.filename,
        ruta_almacenamiento=save_path,
        tipo_archivo=ext,
        tamaño_bytes=tamaño,
        subido_por=(subido_por or None)
    )

    db.add(nuevo)
    await db.commit()
    await db.refresh(nuevo)

    return ArchivoRead.model_validate(nuevo)



# ---------------------------
#   LISTAR ARCHIVOS (con filtros incluyendo rango de fecha)
# ---------------------------
@router.get("/", response_model=list[ArchivoRead])
async def listar_archivos(
    nombre_archivo: str | None = Query(None),
    tipo_archivo: str | None = Query(None),
    subido_por: str | None = Query(None),
    estado: str | None = Query(None),
    subido_en_inicio: datetime | None = Query(None, description="Fecha/hora inicio (ISO)"),
    subido_en_fin: datetime | None = Query(None, description="Fecha/hora fin (ISO)"),
    db: AsyncSession = Depends(get_db)
):
    # construir consulta dinámica
    query = select(Archivo)
    conditions = []

    if nombre_archivo:
        conditions.append(Archivo.nombre_archivo.ilike(f"%{nombre_archivo}%"))
    if tipo_archivo:
        conditions.append(Archivo.tipo_archivo == tipo_archivo)
    if subido_por:
        conditions.append(Archivo.subido_por == subido_por)
    if estado:
        conditions.append(Archivo.estado == estado)
    if subido_en_inicio:
        conditions.append(Archivo.subido_en >= subido_en_inicio)
    if subido_en_fin:
        conditions.append(Archivo.subido_en <= subido_en_fin)

    if subido_en_inicio and not subido_en_fin:
        raise HTTPException(
            status_code=400,
            detail="Debe especificar la fecha de fin para el rango de subida"
        )

    if conditions:
        query = query.where(and_(*conditions))

    q = await db.execute(query)
    rows = q.scalars().all()

    return [ArchivoRead.model_validate(r) for r in rows]



# ---------------------------
#   OBTENER DETALLE
# ---------------------------
@router.get("/{id_archivo}", response_model=ArchivoRead)
async def obtener_archivo(id_archivo: str, db: AsyncSession = Depends(get_db)):
    q = await db.execute(
        select(Archivo).where(Archivo.id_archivo == id_archivo)
    )
    obj = q.scalar_one_or_none()

    if not obj:
        raise HTTPException(404, "Archivo no encontrado")

    return ArchivoRead.model_validate(obj)



# ---------------------------
#   DESCARGAR ARCHIVO
# ---------------------------
@router.get("/download/{id_archivo}")
async def descargar_archivo(id_archivo: str, db: AsyncSession = Depends(get_db)):
    q = await db.execute(
        select(Archivo).where(Archivo.id_archivo == id_archivo)
    )
    obj = q.scalar_one_or_none()

    if not obj:
        raise HTTPException(404, "Archivo no encontrado")

    if not os.path.exists(obj.ruta_almacenamiento):
        raise HTTPException(500, "El archivo no existe en el servidor")

    return FileResponse(
        path=obj.ruta_almacenamiento,
        media_type="application/octet-stream",
        filename=obj.nombre_archivo
    )



# ---------------------------
#   ACTUALIZAR ARCHIVO
# ---------------------------
@router.put("/{id_archivo}", response_model=ArchivoRead)
async def actualizar_archivo(
    id_archivo: str,
    data: ArchivoUpdate,
    db: AsyncSession = Depends(get_db)
):
    q = await db.execute(
        select(Archivo).where(Archivo.id_archivo == id_archivo)
    )
    obj = q.scalar_one_or_none()

    if not obj:
        raise HTTPException(404, "Archivo no encontrado")

    if data.nombre_archivo is not None:
        obj.nombre_archivo = data.nombre_archivo

    if data.tipo_archivo is not None:
        obj.tipo_archivo = data.tipo_archivo

    if data.estado is not None:
        obj.estado = data.estado

    await db.commit()
    await db.refresh(obj)

    return ArchivoRead.model_validate(obj)



# ---------------------------
#   BAJA LÓGICA
# ---------------------------
@router.patch("/desactivar/{id_archivo}")
async def desactivar_archivo(id_archivo: str, db: AsyncSession = Depends(get_db)):
    q = await db.execute(
        select(Archivo).where(Archivo.id_archivo == id_archivo)
    )
    obj = q.scalar_one_or_none()

    if not obj:
        raise HTTPException(404, "Archivo no encontrado")

    if obj.estado == "inactivo":
        raise HTTPException(
            status_code=400,
            detail="El archivo ya se encuentra inactivo"
        )

    obj.estado = "inactivo"
    await db.commit()

    return {"mensaje": "Archivo desactivado correctamente"}


# ---------------------------
#   REACTIVAR ARCHIVO
# ---------------------------
@router.patch("/activar/{id_archivo}")
async def activar_archivo(id_archivo: str, db: AsyncSession = Depends(get_db)):
    q = await db.execute(
        select(Archivo).where(Archivo.id_archivo == id_archivo)
    )
    obj = q.scalar_one_or_none()

    if not obj:
        raise HTTPException(404, "Archivo no encontrado")

    if obj.estado == "activo":
        raise HTTPException(
            status_code=400,
            detail="El archivo ya se encuentra activo"
        )

    obj.estado = "activo"
    await db.commit()

    return {"mensaje": "Archivo reactivado correctamente"}


# ---------------------------
#   ELIMINAR ARCHIVO (físico + BD)
# ---------------------------
@router.delete("/{id_archivo}")
async def eliminar_archivo(id_archivo: str, db: AsyncSession = Depends(get_db)):
    q = await db.execute(
        select(Archivo).where(Archivo.id_archivo == id_archivo)
    )
    obj = q.scalar_one_or_none()

    if not obj:
        raise HTTPException(404, "Archivo no encontrado")

    try:
        os.remove(obj.ruta_almacenamiento)
    except FileNotFoundError:
        pass

    await db.delete(obj)
    await db.commit()

    return {"mensaje": "Archivo eliminado"}
