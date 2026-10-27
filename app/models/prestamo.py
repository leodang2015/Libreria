from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base

if TYPE_CHECKING:
    from .libro import Libro
    from .socio import Socio


class Prestamo(Base):
    __tablename__ = "prestamos"

    id: Mapped[int] = mapped_column(primary_key=True)
    socio_id: Mapped[int] = mapped_column(ForeignKey("socios.id", ondelete="RESTRICT"), index=True)
    libro_id: Mapped[int] = mapped_column(ForeignKey("libros.id", ondelete="RESTRICT"), index=True)
    fecha_prestamo: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    fecha_limite: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    fecha_devolucion: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    multa: Mapped[float] = mapped_column(Numeric(10, 2, asdecimal=False), default=0.0)
    devuelto: Mapped[bool] = mapped_column(default=False)

    socio: Mapped["Socio"] = relationship(back_populates="prestamos")
    libro: Mapped["Libro"] = relationship(back_populates="prestamos")
