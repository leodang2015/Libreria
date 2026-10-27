from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .libro import LibroLeer
from .socio import SocioResumen


class PrestamoCrear(BaseModel):
    socio_id: int = Field(gt=0)
    libro_id: int = Field(gt=0)
    fecha_limite: datetime


class PrestamoActualizar(BaseModel):
    fecha_devolucion: datetime | None = None
    multa: float | None = Field(default=None, ge=0)
    devuelto: bool | None = None


class PrestamoLeer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    socio_id: int
    libro_id: int
    fecha_prestamo: datetime
    fecha_limite: datetime
    fecha_devolucion: datetime | None
    multa: float
    devuelto: bool
    socio: SocioResumen
    libro: LibroLeer
