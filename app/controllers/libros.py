from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ..core.exceptions import Conflicto, NoEncontrado
from ..models import Autor, Categoria, Libro, Prestamo
from ..schemas.libro import LibroActualizar, LibroCrear


def _consulta_base():
    return select(Libro).options(selectinload(Libro.autor), selectinload(Libro.categorias))


def listar(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    autor_id: int | None = None,
    categoria_id: int | None = None,
    buscar: str | None = None,
) -> list[Libro]:
    consulta = _consulta_base()
    if autor_id is not None:
        consulta = consulta.where(Libro.autor_id == autor_id)
    if categoria_id is not None:
        consulta = consulta.join(Libro.categorias).where(Categoria.id == categoria_id)
    if buscar:
        consulta = consulta.where(Libro.titulo.ilike(f"%{buscar}%"))
    consulta = consulta.order_by(Libro.titulo).offset(skip).limit(limit)
    return list(db.scalars(consulta))


def obtener(db: Session, libro_id: int) -> Libro:
    libro = db.scalar(_consulta_base().where(Libro.id == libro_id))
    if libro is None:
        raise NoEncontrado("Libro no encontrado")
    return libro


def _validar_isbn_unico(db: Session, isbn: str, excluir_id: int | None = None) -> None:
    consulta = select(Libro.id).where(func.lower(Libro.isbn) == isbn.lower())
    if excluir_id is not None:
        consulta = consulta.where(Libro.id != excluir_id)
    if db.scalar(consulta) is not None:
        raise Conflicto(f"Ya existe el libro con ISBN '{isbn}'")


def crear(db: Session, datos: LibroCrear) -> Libro:
    autor = db.get(Autor, datos.autor_id)
    if autor is None:
        raise NoEncontrado("Autor no encontrado")
    categorias = db.scalars(select(Categoria).where(Categoria.id.in_(datos.categoria_ids))).all()
    if len(categorias) != len(set(datos.categoria_ids)):
        raise NoEncontrado("Una de las categorías no existe")
    _validar_isbn_unico(db, datos.isbn)
    libro = Libro(
        titulo=datos.titulo,
        isbn=datos.isbn,
        descripcion=datos.descripcion,
        anio_publicacion=datos.anio_publicacion,
        ejemplares=datos.ejemplares,
        disponible=datos.disponible,
        autor_id=datos.autor_id,
    )
    libro.categorias = list(categorias)
    db.add(libro)
    db.commit()
    return obtener(db, libro.id)


def actualizar(db: Session, libro_id: int, datos: LibroActualizar) -> Libro:
    libro = obtener(db, libro_id)
    cambios = datos.model_dump(exclude_unset=True, exclude_none=True)
    if "autor_id" in cambios:
        autor = db.get(Autor, cambios["autor_id"])
        if autor is None:
            raise NoEncontrado("Autor no encontrado")
    if "categoria_ids" in cambios:
        categorias = db.scalars(select(Categoria).where(Categoria.id.in_(cambios["categoria_ids"]))).all()
        if len(categorias) != len(set(cambios["categoria_ids"])):
            raise NoEncontrado("Una de las categorías no existe")
        libro.categorias = list(categorias)
        cambios.pop("categoria_ids")
    if "isbn" in cambios:
        _validar_isbn_unico(db, cambios["isbn"], excluir_id=libro_id)
    for campo, valor in cambios.items():
        setattr(libro, campo, valor)
    db.commit()
    db.expire(libro)
    return obtener(db, libro_id)


def eliminar(db: Session, libro_id: int) -> None:
    libro = obtener(db, libro_id)
    prestamos = db.scalar(select(func.count(Prestamo.id)).where(Prestamo.libro_id == libro_id))
    if prestamos:
        raise Conflicto(f"El libro tiene {prestamos} préstamo(s); no se puede eliminar")
    db.delete(libro)
    db.commit()
