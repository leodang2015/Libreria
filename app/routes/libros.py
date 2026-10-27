from fastapi import APIRouter, Query, status

from ..controllers import libros as controlador
from ..core.dependencies import SessionDep
from ..schemas.libro import LibroActualizar, LibroCrear, LibroLeer

router = APIRouter(prefix="/libros", tags=["Libros"])


@router.get("", response_model=list[LibroLeer])
def listar_libros(
    db: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    autor_id: int | None = Query(default=None, gt=0),
    categoria_id: int | None = Query(default=None, gt=0),
    buscar: str | None = Query(default=None),
):
    return controlador.listar(db, skip=skip, limit=limit, autor_id=autor_id, categoria_id=categoria_id, buscar=buscar)


@router.get("/{libro_id}", response_model=LibroLeer)
def obtener_libro(libro_id: int, db: SessionDep):
    return controlador.obtener(db, libro_id)


@router.post("", response_model=LibroLeer, status_code=status.HTTP_201_CREATED)
def crear_libro(datos: LibroCrear, db: SessionDep):
    return controlador.crear(db, datos)


@router.patch("/{libro_id}", response_model=LibroLeer)
def actualizar_libro(libro_id: int, datos: LibroActualizar, db: SessionDep):
    return controlador.actualizar(db, libro_id, datos)


@router.delete("/{libro_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_libro(libro_id: int, db: SessionDep):
    controlador.eliminar(db, libro_id)
    return None
