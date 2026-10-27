from pydantic import BaseModel, ConfigDict, Field, field_validator


def limpiar_nombre(valor: str | None) -> str | None:
    return " ".join(valor.split()).capitalize() if valor else valor


class CategoriaCrear(BaseModel):
    nombre: str = Field(min_length=3, max_length=50, examples=["Electrónica"])
    descripcion: str | None = Field(default=None, max_length=200, examples=["Equipos y accesorios"])

    validar_nombre = field_validator("nombre")(limpiar_nombre)


class CategoriaActualizar(BaseModel):
    nombre: str | None = Field(default=None, min_length=3, max_length=50)
    descripcion: str | None = Field(default=None, max_length=200)

    validar_nombre = field_validator("nombre")(limpiar_nombre)


class CategoriaLeer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str | None


class CategoriaResumen(BaseModel):
    """Version corta para anidar dentro de un producto."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
