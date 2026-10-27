from fastapi import APIRouter, Query, status

from ..controllers import autores as controlador
from ..core.dependencies import SessionDep
from ..schemas.autor import AutorActualizar, AutorCrear, AutorLeer

router = APIRouter(prefix="/autores", tags=["Autores"])


@router.get("", response_model=list[AutorLeer])
def listar_autores(
    db: SessionDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    nacionalidad: str | None = Query(default=None),
):
    return controlador.listar(db, skip=skip, limit=limit, nacionalidad=nacionalidad)


@router.get("/{autor_id}", response_model=AutorLeer)
def obtener_autor(autor_id: int, db: SessionDep):
    return controlador.obtener(db, autor_id)


@router.post("", response_model=AutorLeer, status_code=status.HTTP_201_CREATED)
def crear_autor(datos: AutorCrear, db: SessionDep):
    return controlador.crear(db, datos)


@router.patch("/{autor_id}", response_model=AutorLeer)
def actualizar_autor(autor_id: int, datos: AutorActualizar, db: SessionDep):
    return controlador.actualizar(db, autor_id, datos)


@router.delete("/{autor_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_autor(autor_id: int, db: SessionDep):
    controlador.eliminar(db, autor_id)
    return None
