from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..core.exceptions import Conflicto, NoEncontrado
from ..models import Autor, Libro
from ..schemas.autor import AutorActualizar, AutorCrear


def listar(db: Session, skip: int = 0, limit: int = 20, nacionalidad: str | None = None) -> list[Autor]:
    consulta = select(Autor)
    if nacionalidad:
        consulta = consulta.where(func.lower(Autor.nacionalidad) == nacionalidad.lower())
    consulta = consulta.order_by(Autor.nombre).offset(skip).limit(limit)
    return list(db.scalars(consulta))


def obtener(db: Session, autor_id: int) -> Autor:
    autor = db.get(Autor, autor_id)
    if autor is None:
        raise NoEncontrado("Autor no encontrado")
    return autor


def _validar_nombre_unico(db: Session, nombre: str, excluir_id: int | None = None) -> None:
    consulta = select(Autor.id).where(func.lower(Autor.nombre) == nombre.lower())
    if excluir_id is not None:
        consulta = consulta.where(Autor.id != excluir_id)
    if db.scalar(consulta) is not None:
        raise Conflicto(f"Ya existe el autor '{nombre}'")


def crear(db: Session, datos: AutorCrear) -> Autor:
    _validar_nombre_unico(db, datos.nombre)
    autor = Autor(**datos.model_dump())
    db.add(autor)
    db.commit()
    return autor


def actualizar(db: Session, autor_id: int, datos: AutorActualizar) -> Autor:
    autor = obtener(db, autor_id)
    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)
    if "nombre" in cambios:
        _validar_nombre_unico(db, cambios["nombre"], excluir_id=autor_id)
    for campo, valor in cambios.items():
        setattr(autor, campo, valor)
    db.commit()
    return autor


def eliminar(db: Session, autor_id: int) -> None:
    autor = obtener(db, autor_id)
    total = db.scalar(select(func.count(Libro.id)).where(Libro.autor_id == autor_id))
    if total:
        raise Conflicto(f"El autor tiene {total} libro(s); no se puede eliminar")
    db.delete(autor)
    db.commit()
