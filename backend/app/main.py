import logging
from fastapi import FastAPI
from app.core.database import engine, Base
from app.routers.usuarios import router as usuarios_router
from app.routers.pacientes import router as pacientes_router
from app.routers.roles import router as roles_router
from app.routers.usuarios_roles import router as usuarios_roles_router
from app.routers.archivos import router as archivos_router
from app.routers.tipos_observacion import router as tipos_observacion_router
from app.routers.admisiones import router as admisiones_router
from app.routers.diagnosticos_secundarios import router as diagnosticos_secundarios_router
from app.routers.ocr_crudo import router as ocr_crudo_router
from app.routers.observaciones import router as observaciones_router
from app.routers.revision_observaciones import router as revision_observaciones_router
from app.routers.auth import router as auth_router

logger = logging.getLogger("uvicorn.error")
app = FastAPI()

@app.on_event("startup")
async def startup():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Tablas creadas / conexión OK")
    except Exception as e:
        logger.error("No se pudo crear tablas en startup: %s", e)

app.include_router(usuarios_router)
app.include_router(pacientes_router)
app.include_router(roles_router)
app.include_router(usuarios_roles_router)
app.include_router(archivos_router)
app.include_router(tipos_observacion_router)
app.include_router(admisiones_router)
app.include_router(diagnosticos_secundarios_router)
app.include_router(ocr_crudo_router)
app.include_router(observaciones_router)
app.include_router(revision_observaciones_router)
app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "INAAQC backend OK"}