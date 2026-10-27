from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ..core.exceptions import Conflicto, NoEncontrado
from ..models import Producto
from ..schemas.producto import ProductoActualizar, ProductoCrear
from . import categorias as categorias_ctrl


def _consulta_base():
    # selectinload trae la categoria de todos los productos en una sola consulta extra.
    return select(Producto).options(selectinload(Producto.categoria))


def listar(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    categoria_id: int | None = None,
    buscar: str | None = None,
    solo_activos: bool = False,
) -> list[Producto]:
    consulta = _consulta_base()
    if categoria_id is not None:
        consulta = consulta.where(Producto.categoria_id == categoria_id)
    if buscar:
        consulta = consulta.where(Producto.nombre.ilike(f"%{buscar}%"))
    if solo_activos:
        consulta = consulta.where(Producto.activo.is_(True))
    consulta = consulta.order_by(Producto.nombre).offset(skip).limit(limit)
    return list(db.scalars(consulta))


def listar_de_categoria(db: Session, categoria_id: int) -> list[Producto]:
    categorias_ctrl.obtener(db, categoria_id)
    return listar(db, categoria_id=categoria_id, limit=100)


def obtener(db: Session, producto_id: int) -> Producto:
    producto = db.scalar(_consulta_base().where(Producto.id == producto_id))
    if producto is None:
        raise NoEncontrado("Producto no encontrado")
    return producto


def _validar_nombre_unico(db: Session, nombre: str, excluir_id: int | None = None) -> None:
    consulta = select(Producto.id).where(func.lower(Producto.nombre) == nombre.lower())
    if excluir_id is not None:
        consulta = consulta.where(Producto.id != excluir_id)
    if db.scalar(consulta) is not None:
        raise Conflicto(f"Ya existe el producto '{nombre}'")


def crear(db: Session, datos: ProductoCrear) -> Producto:
    categorias_ctrl.obtener(db, datos.categoria_id)
    _validar_nombre_unico(db, datos.nombre)
    producto = Producto(**datos.model_dump())
    db.add(producto)
    db.commit()
    return obtener(db, producto.id)


def actualizar(db: Session, producto_id: int, datos: ProductoActualizar) -> Producto:
    producto = obtener(db, producto_id)
    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)
    if "categoria_id" in cambios:
        categorias_ctrl.obtener(db, cambios["categoria_id"])
    if "nombre" in cambios:
        _validar_nombre_unico(db, cambios["nombre"], excluir_id=producto_id)
    for campo, valor in cambios.items():
        setattr(producto, campo, valor)
    db.commit()
    # expire + obtener: recarga la relacion si cambio categoria_id.
    db.expire(producto)
    return obtener(db, producto_id)


def eliminar(db: Session, producto_id: int) -> None:
    producto = obtener(db, producto_id)
    db.delete(producto)
    db.commit()
