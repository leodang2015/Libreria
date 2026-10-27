from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, String, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base

if TYPE_CHECKING:
    from .autor import Autor
    from .categoria import Categoria
    from .prestamo import Prestamo


libro_categoria = Table(
    "libro_categoria",
    Base.metadata,
    Column("libro_id", ForeignKey("libros.id", ondelete="CASCADE"), primary_key=True),
    Column("categoria_id", ForeignKey("categorias.id", ondelete="CASCADE"), primary_key=True),
)


class Libro(Base):
    __tablename__ = "libros"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(150), index=True)
    isbn: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    descripcion: Mapped[str | None] = mapped_column(String(500), default=None)
    anio_publicacion: Mapped[int | None] = mapped_column(default=None)
    ejemplares: Mapped[int] = mapped_column(default=1)
    disponible: Mapped[int] = mapped_column(default=1)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    autor_id: Mapped[int] = mapped_column(ForeignKey("autores.id", ondelete="RESTRICT"), index=True)

    autor: Mapped["Autor"] = relationship(back_populates="libros")
    categorias: Mapped[list["Categoria"]] = relationship(
        secondary=libro_categoria,
        back_populates="libros",
    )
    prestamos: Mapped[list["Prestamo"]] = relationship(back_populates="libro")
