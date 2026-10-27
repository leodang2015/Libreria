from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .categoria import CategoriaResumen, limpiar_nombre


class ProductoCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=100, examples=["Teclado mecánico"])
    descripcion: str | None = Field(default=None, max_length=300, examples=["Switches rojos, RGB"])
    precio: float = Field(gt=0, le=1_000_000, examples=[149.99])
    stock: int = Field(default=0, ge=0, examples=[10])
    activo: bool = True
    categoria_id: int = Field(gt=0, examples=[1])

    validar_nombre = field_validator("nombre")(limpiar_nombre)


class ProductoActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=100)
    descripcion: str | None = Field(default=None, max_length=300)
    precio: float | None = Field(default=None, gt=0, le=1_000_000)
    stock: int | None = Field(default=None, ge=0)
    activo: bool | None = None
    categoria_id: int | None = Field(default=None, gt=0)

    validar_nombre = field_validator("nombre")(limpiar_nombre)


class ProductoLeer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str | None
    precio: float
    stock: int
    activo: bool
    creado_en: datetime
    categoria: CategoriaResumen
