from pydantic import BaseModel

class RolBase(BaseModel):
    nombre_rol: str

class RolCreate(RolBase):
    pass

class RolUpdate(BaseModel):
    nombre_rol: str | None = None

class RolOut(RolBase):
    id_rol: int

    model_config = {"from_attributes": True}
