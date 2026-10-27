from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..core.exceptions import Conflicto, NoEncontrado
from ..models import Categoria, Libro
from ..schemas.categoria import CategoriaActualizar, CategoriaCrear


def listar(db: Session) -> list[Categoria]:
    return list(db.scalars(select(Categoria).order_by(Categoria.nombre)))


def obtener(db: Session, categoria_id: int) -> Categoria:
    categoria = db.get(Categoria, categoria_id)
    if categoria is None:
        raise NoEncontrado("Categoría no encontrada")
    return categoria


def _validar_nombre_unico(db: Session, nombre: str, excluir_id: int | None = None) -> None:
    consulta = select(Categoria.id).where(func.lower(Categoria.nombre) == nombre.lower())
    if excluir_id is not None:
        consulta = consulta.where(Categoria.id != excluir_id)
    if db.scalar(consulta) is not None:
        raise Conflicto(f"Ya existe la categoría '{nombre}'")


def crear(db: Session, datos: CategoriaCrear) -> Categoria:
    _validar_nombre_unico(db, datos.nombre)
    categoria = Categoria(**datos.model_dump())
    db.add(categoria)
    db.commit()
    return categoria


def actualizar(db: Session, categoria_id: int, datos: CategoriaActualizar) -> Categoria:
    categoria = obtener(db, categoria_id)
    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)
    if "nombre" in cambios:
        _validar_nombre_unico(db, cambios["nombre"], excluir_id=categoria_id)
    for campo, valor in cambios.items():
        setattr(categoria, campo, valor)
    db.commit()
    return categoria


def eliminar(db: Session, categoria_id: int) -> None:
    categoria = obtener(db, categoria_id)
    total = db.scalar(
        select(func.count(Libro.id))
        .join(Libro.categorias)
        .where(Categoria.id == categoria_id)
    )
    if total:
        raise Conflicto(f"La categoría tiene {total} libro(s); no se puede eliminar")
    db.delete(categoria)
    db.commit()
