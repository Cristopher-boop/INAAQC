import os
import uuid
from uuid import UUID
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.archivos import Archivo
from app.schemas.archivos import ArchivoRead

router = APIRouter(prefix="/archivos", tags=["Archivos"])

UPLOAD_DIR = "uploads"

# Crear carpeta si no existe
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ---------------------------
#   SUBIR ARCHIVO
# ---------------------------
@router.post("/upload", response_model=ArchivoRead)
async def subir_archivo(
    archivo: UploadFile = File(...),
    subido_por: str | None = None,  # aceptar None
    db: AsyncSession = Depends(get_db)
):
    # Validar tipo y homogeneizar extension
    ext = archivo.filename.split(".")[-1].lower()
    if ext == "jpeg":
        ext = "jpg"
    if ext not in ("pdf", "jpg", "png"):
        raise HTTPException(400, "Tipo de archivo no permitido (solo pdf,jpg,png)")

    # Nombre interno seguro (no lo convertimos a string-uuid para la BD)
    file_uuid = uuid.uuid4()  # uuid.UUID object
    internal_name = f"{file_uuid}.{ext}"
    save_path = os.path.join(UPLOAD_DIR, internal_name)

    # Guardar archivo físicamente
    content = await archivo.read()
    with open(save_path, "wb") as f:
        f.write(content)

    tamaño = os.path.getsize(save_path)

    # Guardar metadata BD. NO forzamos id_archivo a string; pasamos UUID
    nuevo = Archivo(
        id_archivo=file_uuid,  # UUID object, compatible con Column(UUID(as_uuid=True))
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
#   LISTAR ARCHIVOS
# ---------------------------
@router.get("/", response_model=list[ArchivoRead])
async def listar_archivos(db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(Archivo))
    rows = q.scalars().all()
    return [ArchivoRead.model_validate(r) for r in rows]



# ---------------------------
#   OBTENER DETALLE
# ---------------------------
@router.get("/{id_archivo}", response_model=ArchivoRead)
async def obtener_archivo(id_archivo: str, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(Archivo).where(Archivo.id_archivo == id_archivo))
    obj = q.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Archivo no encontrado")

    return ArchivoRead.model_validate(obj)



# ---------------------------
#   DESCARGAR ARCHIVO
# ---------------------------
@router.get("/download/{id_archivo}")
async def descargar_archivo(id_archivo: str, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(Archivo).where(Archivo.id_archivo == id_archivo))
    obj = q.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Archivo no encontrado")

    if not os.path.exists(obj.ruta_almacenamiento):
        raise HTTPException(500, "El archivo no existe en el servidor")

    # StreamingResponse elimina problemas de memoria
    from fastapi.responses import FileResponse

    return FileResponse(
        path=obj.ruta_almacenamiento,
        media_type="application/octet-stream",
        filename=obj.nombre_archivo
    )



# ---------------------------
#   ELIMINAR ARCHIVO
# ---------------------------
@router.delete("/{id_archivo}")
async def eliminar_archivo(id_archivo: str, db: AsyncSession = Depends(get_db)):
    q = await db.execute(select(Archivo).where(Archivo.id_archivo == id_archivo))
    obj = q.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Archivo no encontrado")

    # borrar archivo físico
    try:
        os.remove(obj.ruta_almacenamiento)
    except FileNotFoundError:
        pass

    await db.delete(obj)
    await db.commit()

    return {"mensaje": "Archivo eliminado"}
