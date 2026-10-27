from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..core.exceptions import Conflicto, NoEncontrado, ReglaNegocio
from ..models import Libro, Prestamo, Socio
from ..schemas.prestamo import PrestamoActualizar, PrestamoCrear


def _consulta_base():
    return select(Prestamo).options(selectinload(Prestamo.socio), selectinload(Prestamo.libro))


def listar(db: Session, skip: int = 0, limit: int = 20) -> list[Prestamo]:
    consulta = _consulta_base().order_by(Prestamo.fecha_prestamo.desc()).offset(skip).limit(limit)
    return list(db.scalars(consulta))


def obtener(db: Session, prestamo_id: int) -> Prestamo:
    prestamo = db.scalar(_consulta_base().where(Prestamo.id == prestamo_id))
    if prestamo is None:
        raise NoEncontrado("Préstamo no encontrado")
    return prestamo


def crear(db: Session, datos: PrestamoCrear) -> Prestamo:
    socio = db.get(Socio, datos.socio_id)
    if socio is None:
        raise NoEncontrado("Socio no encontrado")
    libro = db.get(Libro, datos.libro_id)
    if libro is None:
        raise NoEncontrado("Libro no encontrado")
    if libro.disponible <= 0:
        raise ReglaNegocio("No hay ejemplares disponibles para ese libro")
    if not socio.activo:
        raise ReglaNegocio("El socio no está activo")

    prestamo = Prestamo(
        socio_id=datos.socio_id,
        libro_id=datos.libro_id,
        fecha_limite=datos.fecha_limite,
    )
    libro.disponible -= 1
    db.add(prestamo)
    db.commit()
    return obtener(db, prestamo.id)


def actualizar(db: Session, prestamo_id: int, datos: PrestamoActualizar) -> Prestamo:
    prestamo = obtener(db, prestamo_id)
    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)
    if "fecha_devolucion" in cambios:
        prestamo.fecha_devolucion = cambios["fecha_devolucion"]
        prestamo.devuelto = True
        if prestamo.fecha_devolucion > prestamo.fecha_limite:
            dias = (prestamo.fecha_devolucion - prestamo.fecha_limite).days
            prestamo.multa = max(dias * 1000, 0)
        prestamo.libro.disponible += 1
    if "multa" in cambios:
        prestamo.multa = cambios["multa"]
    if "devuelto" in cambios:
        prestamo.devuelto = cambios["devuelto"]
    db.commit()
    return obtener(db, prestamo_id)


def eliminar(db: Session, prestamo_id: int) -> None:
    prestamo = obtener(db, prestamo_id)
    if prestamo.devuelto is False:
        raise Conflicto("No se puede eliminar un préstamo activo")
    db.delete(prestamo)
    db.commit()
