from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..core.exceptions import Conflicto, NoEncontrado
from ..models import Prestamo, Socio
from ..schemas.socio import SocioActualizar, SocioCrear


def listar(db: Session, skip: int = 0, limit: int = 20) -> list[Socio]:
    return list(db.scalars(select(Socio).order_by(Socio.nombre).offset(skip).limit(limit)))


def obtener(db: Session, socio_id: int) -> Socio:
    socio = db.get(Socio, socio_id)
    if socio is None:
        raise NoEncontrado("Socio no encontrado")
    return socio


def _validar_email_unico(db: Session, email: str, excluir_id: int | None = None) -> None:
    consulta = select(Socio.id).where(func.lower(Socio.email) == email.lower())
    if excluir_id is not None:
        consulta = consulta.where(Socio.id != excluir_id)
    if db.scalar(consulta) is not None:
        raise Conflicto(f"Ya existe un socio con el email '{email}'")


def crear(db: Session, datos: SocioCrear) -> Socio:
    _validar_email_unico(db, datos.email)
    socio = Socio(**datos.model_dump())
    db.add(socio)
    db.commit()
    return socio


def actualizar(db: Session, socio_id: int, datos: SocioActualizar) -> Socio:
    socio = obtener(db, socio_id)
    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)
    if "email" in cambios:
        _validar_email_unico(db, cambios["email"], excluir_id=socio_id)
    for campo, valor in cambios.items():
        setattr(socio, campo, valor)
    db.commit()
    return socio


def eliminar(db: Session, socio_id: int) -> None:
    socio = obtener(db, socio_id)
    total = db.scalar(select(func.count(Prestamo.id)).where(Prestamo.socio_id == socio_id))
    if total:
        raise Conflicto(f"El socio tiene {total} préstamo(s); no se puede eliminar")
    db.delete(socio)
    db.commit()
